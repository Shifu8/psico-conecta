param([string]$BucketName = "psicoconecta-frontend-108631844312", [string]$Region = "us-east-2")

# Disable Block Public Access
aws s3api put-public-access-block --bucket $BucketName --public-access-block-configuration "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false" --region $Region

# Configure Website Hosting (SPA routing)
aws s3 website "s3://$BucketName" --index-document index.html --error-document index.html --region $Region

# Apply Public Read Policy
$policy = @"
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::$BucketName/*"
    }
  ]
}
"@

$tempFile = [System.IO.Path]::GetTempFileName() + ".json"
$policy | Set-Content -Path $tempFile -Encoding UTF8
aws s3api put-bucket-policy --bucket $BucketName --policy file://$tempFile --region $Region
Remove-Item $tempFile -Force -ErrorAction SilentlyContinue

Write-Host "Bucket S3 $BucketName configurado como sitio web publico." -ForegroundColor Green
