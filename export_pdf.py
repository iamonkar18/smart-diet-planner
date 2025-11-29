import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def build_pdf(plan_df, summary_dict, user_name: str, date_str: str) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 50
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, y, f"Smart Diet Planner - {user_name}")
    y -= 25
    c.setFont("Helvetica", 12)
    c.drawString(40, y, f"Date: {date_str}")
    y -= 30

    # Summary
    c.setFont("Helvetica-Bold", 13)
    c.drawString(40, y, "Daily Summary:")
    y -= 18
    c.setFont("Helvetica", 11)
    for key, val in summary_dict.items():
        c.drawString(50, y, f"{key}: {val}")
        y -= 14

    y -= 15
    c.setFont("Helvetica-Bold", 13)
    c.drawString(40, y, "Meal Plan:")
    y -= 18
    c.setFont("Helvetica", 10)

    cols = ["meal_type", "food", "serving", "servings", "calories"]
    for _, row in plan_df[cols].iterrows():
        line = f"{row['meal_type']}: {row['food']} ({row['serving']}) x{row['servings']} -> {row['calories']} kcal"
        c.drawString(45, y, line[:110])
        y -= 12
        if y < 50:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica", 10)

    c.showPage()
    c.save()
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

