from django.db import models

class Report(models.Model):
    reporter = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    content_type = models.CharField(max_length=100)
    object_id = models.PositiveIntegerField()
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class DMCA(models.Model):
    claimant = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Flag(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    reason = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

class SecuritySetting(models.Model):
    id = models.AutoField(primary_key=True)
    max_file_size_mb = models.PositiveIntegerField(default=20, help_text="Maximum upload file size in MB")
    allowed_mime_types = models.TextField(
        default='application/sla,application/vnd.ms-pki.stl,application/octet-stream,image/jpeg,image/png',
        help_text="Comma-separated list of allowed MIME types"
    )

    def get_allowed_mime_types(self):
        return [mime.strip() for mime in self.allowed_mime_types.split(',') if mime.strip()]

    def __str__(self):
        return f"Security Settings (ID: {self.id})"

    class Meta:
        verbose_name = "Security Setting"
        verbose_name_plural = "Security Settings"
