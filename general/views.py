import qrcode
from io import BytesIO
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from manager.models import Patient # type: ignore


def download_qr_code(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id, hospital=request.user.hospital)
    patient_detail_url = request.build_absolute_uri(f"/patients/{patient.id}/")
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(patient_detail_url)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    response = HttpResponse(buffer.getvalue(), content_type='image/png')
    response['Content-Disposition'] = f'attachment; filename="patient_{patient.mrn}_qrcode.png"'
    return response
