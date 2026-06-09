def generate_cover_letter(full_name: str, profile: str, job_title: str, company: str, job_description: str) -> str:
    company_line = company or "your organisation"
    return f"""Dear Hiring Manager,

I am writing to apply for the {job_title} opportunity at {company_line}. I am interested in this role because it aligns with my background, skills, and career goal of gaining practical experience in the ICT field.

My profile includes {profile[:500]}. Based on the job requirements, I believe I can contribute through my willingness to learn, technical foundation, problem-solving ability, and commitment to delivering quality work.

I would appreciate the opportunity to be considered for this position and to further discuss how my skills and studies align with your organisation's needs.

Kind regards,
{full_name}
"""
