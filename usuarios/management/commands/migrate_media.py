from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand

from usuarios.models import Usuario, Producto


class Command(BaseCommand):
    help = 'Migra archivos de media locales a storage por defecto (Cloudinary si está configurado)'

    def handle(self, *args, **options):
        media_root = Path(settings.MEDIA_ROOT)
        migrated = 0

        targets = [
            (Usuario, 'foto_perfil'),
            (Producto, 'imagen'),
        ]

        for model, field_name in targets:
            qs = model.objects.exclude(**{f"{field_name}__isnull": True}).exclude(**{f"{field_name}": ""})
            for obj in qs:
                field = getattr(obj, field_name)
                name = field.name
                if not name:
                    continue
                local_path = media_root / name
                if local_path.exists():
                    with local_path.open('rb') as f:
                        saved_name = default_storage.save(name, File(f))
                        setattr(obj, field_name, saved_name)
                        obj.save()
                        self.stdout.write(self.style.NOTICE(f"Migrado {model.__name__} id={obj.id} -> {saved_name}"))
                        migrated += 1

        self.stdout.write(self.style.SUCCESS(f"Archivos migrados: {migrated}"))
