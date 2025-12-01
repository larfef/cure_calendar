import qrcode
from qrcode.image import svg


def qr_from_url(url, box_size=5):
    qr = qrcode.QRCode(
        image_factory=svg.SvgPathImage,
        box_size=box_size,
        border=0,
    )
    qr.add_data(url)
    qr.make(fit=True)
    qr_img = qr.make_image()
    qr_img = qr_img.to_string(encoding="unicode")

    return qr_img
