import xml.etree.ElementTree as ET
import uuid
from django.core.files import File
from io import BytesIO
import qrcode
from django.core.management.base import BaseCommand
from agaclar.models import Agac, Arazi

class Command(BaseCommand):
    help = 'Imports trees from a KML file into the database.'

    def add_arguments(self, parser):
        parser.add_argument('kml_file_path', type=str, help='The path to the KML file.')
        parser.add_argument('arazi_id', type=str, help='The ID of the Arazi.')

    def handle(self, *args, **kwargs):
        kml_file_path = kwargs['kml_file_path']
        arazi_id = kwargs['arazi_id']
        self.import_kml_to_db(kml_file_path, arazi_id)

    def import_kml_to_db(self, kml_file_path, arazi_id):
        try:
            arazi = Arazi.objects.get(id=uuid.UUID(arazi_id))
        except Arazi.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Arazi with ID {arazi_id} does not exist.'))
            return

        tree = ET.parse(kml_file_path)
        root = tree.getroot()

        namespace = {'ns': 'http://www.opengis.net/kml/2.2'}

        for placemark in root.findall(".//ns:Placemark", namespace):
            coordinates = placemark.find(".//ns:coordinates", namespace).text.strip()

            try:
                latitude, longitude, _ = map(float, coordinates.replace('°', '').replace('N', '').replace('E', '').replace('S', '').replace('W', '').strip().split(","))

                agac = Agac(
                    id=uuid.uuid4(),
                    arazi=arazi,
                    alatitude=latitude,
                    alongitude=longitude,
                )

                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr_url = f"http://127.0.0.1:8000/agac_detay/{agac.id}"  # example.com yerine kendi alan adınızı ve yolunuzu yazın
                qr.add_data(qr_url)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")

                buffer = BytesIO()
                img.save(buffer, format="PNG")
                file_name = f"qrcode_{agac.id}.png"
                agac.qr_code.save(file_name, File(buffer), save=False)

                agac.save()
                self.stdout.write(self.style.SUCCESS(f'Tree with ID {agac.id} added successfully.'))
            except ValueError as e:
                self.stdout.write(self.style.ERROR(f'Error processing tree: {e}'))

