from django.core.exceptions import ValidationError
from utils.virus_scan import scan_file_with_clamav

from django import forms

class VirusScanMixin(forms.Form):
    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('file')
        if file:
            # Save file temporarily to scan
            import tempfile
            with tempfile.NamedTemporaryFile(delete=True) as tmp:
                for chunk in file.chunks():
                    tmp.write(chunk)
                tmp.flush()
                is_clean, output = scan_file_with_clamav(tmp.name)
                if not is_clean:
                    raise ValidationError(f"Virus detected in uploaded file!\n{output}")
        return cleaned_data
