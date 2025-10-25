"""
S3/MinIO storage service for thumbnails
"""
import structlog
import boto3
from botocore.exceptions import ClientError
from typing import Optional
from io import BytesIO

from ..core.config import settings

logger = structlog.get_logger()


class StorageService:
    """
    S3/MinIO storage service for ad thumbnails
    """

    def __init__(self):
        # Initialize S3 client
        if settings.S3_ENDPOINT:
            # MinIO or custom S3-compatible storage
            self.client = boto3.client(
                's3',
                endpoint_url=settings.S3_ENDPOINT,
                aws_access_key_id=settings.S3_ACCESS_KEY,
                aws_secret_access_key=settings.S3_SECRET_KEY,
                region_name=settings.S3_REGION
            )
        else:
            # AWS S3
            self.client = boto3.client(
                's3',
                aws_access_key_id=settings.S3_ACCESS_KEY,
                aws_secret_access_key=settings.S3_SECRET_KEY,
                region_name=settings.S3_REGION
            )

        self.bucket = settings.S3_BUCKET

    def ensure_bucket(self):
        """Ensure the bucket exists, create if not"""
        try:
            self.client.head_bucket(Bucket=self.bucket)
            logger.info("storage_bucket_exists", bucket=self.bucket)
        except ClientError:
            try:
                self.client.create_bucket(Bucket=self.bucket)
                logger.info("storage_bucket_created", bucket=self.bucket)
            except ClientError as e:
                logger.error("storage_bucket_create_failed", bucket=self.bucket, error=str(e))

    def upload_thumbnail(
        self,
        file_data: bytes,
        filename: str,
        content_type: str = "image/jpeg"
    ) -> Optional[str]:
        """
        Upload thumbnail to S3/MinIO

        Args:
            file_data: Image bytes
            filename: Filename (e.g., "ad-uuid.jpg")
            content_type: MIME type

        Returns:
            Public URL or None if failed
        """
        try:
            self.client.put_object(
                Bucket=self.bucket,
                Key=filename,
                Body=BytesIO(file_data),
                ContentType=content_type,
                ACL='public-read'  # Make publicly accessible
            )

            # Generate URL
            if settings.S3_ENDPOINT:
                url = f"{settings.S3_ENDPOINT}/{self.bucket}/{filename}"
            else:
                url = f"https://{self.bucket}.s3.{settings.S3_REGION}.amazonaws.com/{filename}"

            logger.info("thumbnail_uploaded", filename=filename, url=url)
            return url

        except ClientError as e:
            logger.error("thumbnail_upload_failed", filename=filename, error=str(e))
            return None

    def delete_thumbnail(self, filename: str) -> bool:
        """
        Delete thumbnail from S3/MinIO

        Args:
            filename: Filename to delete

        Returns:
            True if successful
        """
        try:
            self.client.delete_object(Bucket=self.bucket, Key=filename)
            logger.info("thumbnail_deleted", filename=filename)
            return True
        except ClientError as e:
            logger.error("thumbnail_delete_failed", filename=filename, error=str(e))
            return False
