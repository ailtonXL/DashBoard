from django.core.management.base import BaseCommand

from core.models import Atestado


class Command(BaseCommand):
    help = 'Criptografa campos sensíveis dos atestados já existentes no banco'

    def handle(self, *args, **options):
        docs = Atestado.objects.all().order_by('id')
        total = docs.count()

        if total == 0:
            self.stdout.write(self.style.WARNING('Nenhum atestado encontrado para criptografar.'))
            return

        self.stdout.write(self.style.WARNING(f'Iniciando criptografia de {total} registro(s)...'))

        for idx, doc in enumerate(docs, start=1):
            doc.save()
            self.stdout.write(f'[{idx}/{total}] Registro ID={doc.id} criptografado.')

        self.stdout.write(self.style.SUCCESS('Criptografia concluída com sucesso.'))
