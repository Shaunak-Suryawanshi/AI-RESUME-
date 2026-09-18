from io import BytesIO


def test_resume_upload_rejects_non_pdf_content(client, auth_headers):
    response = client.post(
        "/api/resumes",
        data={"file": (BytesIO(b"not a PDF"), "resume.pdf")},
        headers=auth_headers,
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    assert response.json["error"] == "Uploaded file is not a valid PDF"


def test_resume_upload_accepts_pdf_signature(client, auth_headers):
    response = client.post(
        "/api/resumes",
        data={"file": (BytesIO(b"%PDF-1.4\nminimal"), "resume.pdf")},
        headers=auth_headers,
        content_type="multipart/form-data",
    )
    assert response.status_code == 201
    assert response.json["original_filename"] == "resume.pdf"
    assert response.json["processing_status"] == "pending"
