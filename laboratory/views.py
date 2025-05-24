# laboratory/views.py

import uuid
from io import BytesIO
import io
import base64

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView, ListView
from django.template.loader import render_to_string
from django.core.files.base import ContentFile

from manager.models import Patient
from .models import TestOrder, LabRequest, TestGroup, Sample, Test
from .forms import TestOrderForm, TestForm, TestGroupForm
import qrcode


def testorder_add(request):
    """
    Stage 1: Submit a new TestOrder or LabRequest for a given patient (via ?patient=<id>).
    """
    patient_id = request.GET.get('patient')
    patient = get_object_or_404(Patient, id=patient_id)

    if request.method == 'POST':
        form = TestOrderForm(request.POST)
        if form.is_valid():
            # Check which type of request to create
            request_type = request.POST.get('request_type', 'order')
            
            if request_type == 'order':
                # Create a TestOrder
                order = form.save(commit=False)
                order.patient = patient
                order.save()
                form.save_m2m()
                messages.success(request, "Lab order submitted.")
            else:
                # Create a LabRequest
                lab_request = LabRequest(
                    patient=patient,
                    group=form.cleaned_data.get('group')
                )
                lab_request.save()
                
                # Add selected tests
                for test in form.cleaned_data.get('tests'):
                    lab_request.tests.add(test)
                
                messages.success(request, "Lab request with QR tracking submitted.")
            
            return redirect('manager:patient_detail', pk=patient.id)
    else:
        form = TestOrderForm()

    return render(request, 'laboratory/testorder_form.html', {
        'form': form,
        'patient': patient,
    })


def testorder_print(request, pk):
    """
    Show (or PDF-render) the TestOrder + its samples' QR codes.
    """
    order = get_object_or_404(TestOrder, pk=pk)

    # Attempt to import WeasyPrint here, so missing libraries won't break startup
    try:
        from weasyprint import HTML
    except Exception:
        HTML = None

    if HTML:
        html_string = render_to_string('laboratory/testorder_print.html', {
            'order': order,
        })
        html = HTML(
            string=html_string,
            base_url=request.build_absolute_uri('/')
        )
        pdf = html.write_pdf()
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="order-{order.id}.pdf"'
        return response

    # Fallback: normal HTML page
    return render(request, "laboratory/testorder_print.html", {
        "order": order,
    })


def sample_scan(request, token):
    """
    When a sample QR is scanned, redirect to its parent order's print view.
    """
    sample = get_object_or_404(Sample, token=token)
    return redirect('laboratory:testorder_print', pk=sample.test_order.pk)


def sample_barcode_print(request, sample_id):
    """
    Render a page (or PDF) showing just the sample's QR code.
    """
    sample = get_object_or_404(Sample, id=sample_id)

    try:
        from weasyprint import HTML
    except Exception:
        HTML = None

    if HTML:
        html_string = render_to_string('laboratory/sample_barcode_print.html', {
            'sample': sample,
        })
        html = HTML(
            string=html_string,
            base_url=request.build_absolute_uri('/')
        )
        pdf = html.write_pdf()
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="sample-{sample.id}.pdf"'
        return response

    return render(request, 'laboratory/sample_barcode_print.html', {
        'sample': sample,
    })


class LabRequestCreateView(CreateView):
    """
    4-stage LabRequest workflow: submitted → accepted → collected → completed
    """
    model = LabRequest
    fields = ['patient', 'group', 'tests']
    template_name = "laboratory/lab_request_form.html"

    def get_initial(self):
        init = super().get_initial()
        if 'patient' in self.request.GET:
            init['patient'] = self.request.GET['patient']
        if 'group' in self.request.GET:
            init['group'] = self.request.GET['group']
        return init

    def get_success_url(self):
        return reverse('laboratory:lab_request_detail', args=[self.object.pk])


class LabRequestDetailView(DetailView):
    """
    Shows the current status & QR-token of a LabRequest.
    """
    model = LabRequest
    template_name = "laboratory/lab_request_detail.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get the request object
        lab_request = self.object
        
        # Generate the scan URL
        scan_url = reverse('laboratory:lab_request_scan', args=[lab_request.token])
        context['scan_url'] = scan_url
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=1)
        qr.add_data(self.request.build_absolute_uri(scan_url))
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert QR code to base64 for embedding in HTML
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        qr_code_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        context['qr_code_data'] = f"data:image/png;base64,{qr_code_base64}"
        
        return context


def lab_request_scan(request, token):
    """
    Each QR scan advances the LabRequest to its next status.
    """
    req = get_object_or_404(LabRequest, token=token)

    if req.status == req.STATUS_SUBMITTED:
        req.status = req.STATUS_ACCEPTED
    elif req.status == req.STATUS_ACCEPTED:
        req.status = req.STATUS_COLLECTED
        req.token = uuid.uuid4()  # regenerate token if needed
    elif req.status == req.STATUS_COLLECTED:
        req.status = req.STATUS_COMPLETED

    req.save()
    return redirect('laboratory:lab_request_detail', pk=req.pk)


# Test Management Views
class TestListView(ListView):
    """
    Lists all available tests with search and category filtering
    """
    model = Test
    template_name = 'laboratory/test_list.html'
    context_object_name = 'tests'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get unique categories for filter dropdown
        categories = Test.objects.exclude(main_category__isnull=True).values_list(
            'main_category', flat=True).distinct()
        context['categories'] = categories
        return context


class TestCreateView(CreateView):
    """
    Creates a new test
    """
    model = Test
    form_class = TestForm
    template_name = 'laboratory/test_form.html'
    success_url = reverse_lazy('laboratory:test_list')

    def form_valid(self, form):
        messages.success(self.request, "Test added successfully.")
        return super().form_valid(form)


class TestUpdateView(UpdateView):
    """
    Updates an existing test
    """
    model = Test
    form_class = TestForm
    template_name = 'laboratory/test_form.html'
    success_url = reverse_lazy('laboratory:test_list')

    def form_valid(self, form):
        messages.success(self.request, "Test updated successfully.")
        return super().form_valid(form)


class TestDeleteView(DeleteView):
    """
    Deletes a test
    """
    model = Test
    success_url = reverse_lazy('laboratory:test_list')
    template_name = 'laboratory/test_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Test deleted successfully.")
        return super().delete(request, *args, **kwargs)


# Test Group Management Views
class TestGroupListView(ListView):
    """
    Lists all test groups
    """
    model = TestGroup
    template_name = 'laboratory/test_group_list.html'
    context_object_name = 'groups'
    
    def render_to_response(self, context, **response_kwargs):
        """
        Return a JSON response if requested, otherwise render the template.
        """
        if self.request.GET.get('format') == 'json':
            groups_data = []
            for group in context['groups']:
                groups_data.append({
                    'id': group.id,
                    'name': group.name,
                    'tests': list(group.tests.values_list('id', flat=True))
                })
            
            return JsonResponse(groups_data, safe=False)
        
        return super().render_to_response(context, **response_kwargs)


class TestGroupCreateView(CreateView):
    """
    Creates a new test group
    """
    model = TestGroup
    form_class = TestGroupForm
    template_name = 'laboratory/test_group_form.html'
    success_url = reverse_lazy('laboratory:test_group_list')

    def form_valid(self, form):
        messages.success(self.request, "Test group created successfully.")
        return super().form_valid(form)


class TestGroupUpdateView(UpdateView):
    """
    Updates an existing test group
    """
    model = TestGroup
    form_class = TestGroupForm
    template_name = 'laboratory/test_group_form.html'
    success_url = reverse_lazy('laboratory:test_group_list')

    def form_valid(self, form):
        messages.success(self.request, "Test group updated successfully.")
        return super().form_valid(form)


class TestGroupDeleteView(DeleteView):
    """
    Deletes a test group
    """
    model = TestGroup
    success_url = reverse_lazy('laboratory:test_group_list')
    template_name = 'laboratory/test_group_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Test group deleted successfully.")
        return super().delete(request, *args, **kwargs)
