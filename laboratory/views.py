# laboratory/views.py

import uuid
from io import BytesIO

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponse
from django.views.generic import CreateView, DetailView
from django.template.loader import render_to_string
from django.core.files.base import ContentFile

from manager.models import Patient
from .models import TestOrder, LabRequest, TestGroup, Sample
from .forms import TestOrderForm


def testorder_add(request):
    """
    Stage 1: Submit a new TestOrder for a given patient (via ?patient=<id>).
    """
    patient_id = request.GET.get('patient')
    patient = get_object_or_404(Patient, id=patient_id)

    if request.method == 'POST':
        form = TestOrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.patient = patient
            order.save()
            form.save_m2m()
            messages.success(request, "Lab order submitted.")
            return redirect('manager:patient_detail', pk=patient.id)
    else:
        form = TestOrderForm()

    return render(request, 'laboratory/testorder_form.html', {
        'form': form,
        'patient': patient,
    })


def testorder_print(request, pk):
    """
    Show (or PDF-render) the TestOrder + its samples’ QR codes.
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
    When a sample QR is scanned, redirect to its parent order’s print view.
    """
    sample = get_object_or_404(Sample, token=token)
    return redirect('laboratory:testorder_print', pk=sample.test_order.pk)


def sample_barcode_print(request, sample_id):
    """
    Render a page (or PDF) showing just the sample’s QR code.
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
