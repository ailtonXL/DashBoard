"""
Comando para reprocessar documentos antigos e calcular métri cas.
Útil quando há documentos criados antes da implementação da lógica automática.
"""
from django.core.management.base import BaseCommand
from core.models import Atestado


class Command(BaseCommand):
    help = 'Reprocessa documentos antigos e calcula dias_afastado e absenteismo'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Reprocessa todos os documentos, mesmo os já processados',
        )

    def handle(self, *args, **options):
        if options['all']:
            documentos = Atestado.objects.all()
            self.stdout.write(self.style.WARNING('Reprocessando TODOS os documentos...'))
        else:
            documentos = Atestado.objects.filter(processado=False)
            self.stdout.write(self.style.WARNING('Reprocessando documentos não processados...'))

        total = documentos.count()
        
        if total == 0:
            self.stdout.write(self.style.SUCCESS('✅ Nenhum documento para reprocessar.'))
            return

        for i, doc in enumerate(documentos, 1):
            doc.calcular_metricas()
            doc.save()
            self.stdout.write(
                f"[{i}/{total}] ✓ {doc.nome}: "
                f"dias={doc.dias_afastado}, absenteismo={doc.absenteismo}%"
            )

        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Reprocessamento concluído! {total} documentos atualizados.')
        )
