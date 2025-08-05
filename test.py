import ollama
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
import textwrap
import traceback

# def get_clause_from_ollama(prompt, model='llama3.2:1b'):
#     try:
#         response = ollama.chat(
#             model=model,
#             messages=[{"role": "user", "content": prompt}]
#         )
#         print("✅ Ollama responded.")
#         return response['message']['content']
#     except Exception as e:
#         print("❌ Error from Ollama:", e)
#         traceback.print_exc()
#         return "Error generating clause."

def text_to_pdf(text, output_file):
    from reportlab.lib.pagesizes import LETTER
    from reportlab.pdfgen import canvas
    import re

    c = canvas.Canvas(output_file, pagesize=LETTER)
    width, height = LETTER
    margin = 50
    y = height - margin
    line_height = 18
    max_chars_per_line = 90

    # Draw title only once on the first page
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 30, "Confidentiality Clause")
    y = height - 60  # below title

    first_page = True  # flag to control title drawing

    for paragraph in text.split("\n"):
        wrapped_lines = textwrap.wrap(paragraph, width=max_chars_per_line)
        for line in wrapped_lines:
            if y < margin:
                c.showPage()
                y = height - 60
                first_page = False  # this is now a new page, not the first one

            x = margin
            tokens = re.split(r'(\*\*.*?\*\*)', line)

            for token in tokens:
                if token.startswith("**") and token.endswith("**"):
                    content = token[2:-2]
                    c.setFont("Helvetica-Bold", 12)
                else:
                    content = token
                    c.setFont("Times-Roman", 12)

                c.drawString(x, y, content)
                x += c.stringWidth(content, c._fontname, 12)

            y -= line_height
        # No extra space between paragraphs

    c.save()







# --- Main ---
# prompt = "Generate a confidentiality clause for a SaaS contract, wrap titles and headers with **text**"
# clause = get_clause_from_ollama(prompt)
text='''Given the user's intent to create a "Pani Puri Consumption Clause" and the examples pointing to formal legal documents (SEC S-4/A exhibits), the clause should adopt a formal, structured, and legally-styled tone, even if the subject matter is whimsical. The provided examples are references to exhibits in a corporate filing, which typically include agreements, bylaws, and other legally binding documents. Here's a draft clause, incorporating elements of legal drafting while addressing the "Pani Puri" theme: --- **PANI PURI CONSUMPTION CLAUSE** This Pani Puri Consumption Clause (this "Clause") sets forth the terms and conditions governing the consumption of Pani Puri by any individual, entity, or group (each, a "Consumer") from any vendor, establishment, or provider (each, a "Vendor"). **1. Definitions.** * **(a) "Pani Puri"** shall mean the culinary dish consisting of hollow, crispy fried spheres (puri) filled with spiced mashed potatoes, chickpeas, tamarind chutney, chili, chaat masala, and flavored water (pani), prepared for immediate consumption. * **(b) "Consumption Event"** shall mean any instance, occasion, or period during which Pani Puri is offered and consumed. * **(c) "Consumption Standard"** shall mean the generally accepted practices of hygiene, preparation, and serving applicable to street food or similar culinary offerings in the relevant jurisdiction. **2. Right to Consume.** Subject to the terms and conditions set forth in this Clause, a Consumer shall have the right to consume Pani Puri offered by a Vendor during a Consumption Event, provided that the Consumer tenders the agreed-upon consideration (e.g., payment, exchange, or specific performance as mutually agreed). **3. Conditions Precedent to Consumption.** The right to consume Pani Puri is contingent upon and subject to the satisfaction of the following conditions: * **(a) Vendor Compliance:** The Pani Puri must be prepared and served by a Vendor operating in substantial compliance with the Consumption Standard. * **(b) Consumer Acceptance:** The Consumer, by initiating consumption, acknowledges and accepts the Pani Puri "as-is," including but not limited to its spice level, temperature, and ingredient composition. * **(c) Capacity:** The Consumer represents and warrants that they possess the physical and mental capacity to consume Pani Puri. **4. Limitations and Disclaimers.** * **(a) Quantity:** Unless otherwise expressly agreed in writing, this Clause does not guarantee a specific quantity of Pani Puri available for consumption or limit the quantity that may be consumed, subject always to the Vendor's sole discretion and availability. * **(b) Culinary Variation:** The Consumer acknowledges that variations in taste, spice level, and ingredient proportions are inherent to Pani Puri and shall not constitute a breach of this Clause. * **(c) Health Disclaimer:** The Vendor hereby disclaims, and the Consumer hereby waives and releases the Vendor from, any and all liability for any adverse health effects, digestive discomfort, or allergic reactions arising from the consumption of Pani Puri, unless such effects are directly and solely attributable to the Vendor's gross negligence or willful misconduct in the preparation or handling of the Pani Puri. The Consumer assumes all risks associated with the consumption of Pani Puri. **5. Post-Consumption Obligations.** Following consumption, the Consumer shall be responsible for the proper disposal of any waste generated (e.g., empty puri shells, napkins) in designated receptacles, if available, or in a manner that does not cause undue litter or inconvenience. **6. Governing Law.** This Clause shall be governed by, and construed in accordance with, the laws of the State of Maharashtra, India, without regard to its conflict of laws principles. **7. Entire Clause.** This Clause constitutes the entire understanding and agreement between the Consumer and the Vendor with respect to the subject matter hereof and supersedes all prior discussions, negotiations, and agreements, whether oral or written, relating to the consumption of Pani Puri. --- '''
# print("Generated clause:\n", clause)
text_to_pdf(text, "generated_clause.pdf")
print("✅ PDF saved as 'generated_clause.pdf'")
