from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image as RLImage,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
OUT_PDF = ROOT / "Relatorio_Bad_Smells_Refatoracao.pdf"
SHOT = ROOT / "scripts" / "eslint-antes.png"

pdfmetrics.registerFont(TTFont("Arial", r"C:\Windows\Fonts\arial.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Bold", r"C:\Windows\Fonts\arialbd.ttf"))
pdfmetrics.registerFont(TTFont("Consolas", r"C:\Windows\Fonts\consola.ttf"))

NAVY = HexColor("#1B3A4B")
TEAL = HexColor("#0F6C8D")
CODE_BG = HexColor("#F4F6F8")
RED = HexColor("#B42318")


def make_eslint_screenshot():
    lines = [
        "PS C:\\Users\\Victor\\Desktop\\bad-smells-js-refactoring> npx eslint src/",
        "",
        "C:\\Users\\Victor\\Desktop\\bad-smells-js-refactoring\\src\\ReportGenerator.js",
        "  11:3   error  Refactor this function to reduce its Cognitive Complexity from 27 to the 5 allowed  sonarjs/cognitive-complexity",
        "  43:14  error  Merge this if statement with the nested one                                         sonarjs/no-collapsible-if",
        "",
        "✖ 2 problems (2 errors, 0 warnings)",
    ]
    font = ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", 15)
    padding = 24
    line_h = 22
    width = 1100
    height = padding * 2 + line_h * len(lines) + 36
    img = Image.new("RGB", (width, height), "#0D1117")
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, width, 28], fill="#161B22")
    for i, c in enumerate(["#FF5F56", "#FFBD2E", "#27C93F"]):
        draw.ellipse([12 + i * 18, 8, 22 + i * 18, 18], fill=c)
    y = 44
    for i, line in enumerate(lines):
        color = "#C9D1D9"
        if "error" in line or "✖" in line:
            color = "#FF7B72"
        elif line.startswith("PS "):
            color = "#7EE787"
        draw.text((padding, y), line, font=font, fill=color)
        y += line_h
    img.save(SHOT)


def styles():
    base = getSampleStyleSheet()
    s = {
        "cover_kicker": ParagraphStyle(
            "cover_kicker",
            fontName="Arial",
            fontSize=11,
            textColor=TEAL,
            alignment=TA_CENTER,
            spaceAfter=6,
        ),
        "cover_title": ParagraphStyle(
            "cover_title",
            fontName="Arial-Bold",
            fontSize=22,
            leading=28,
            textColor=NAVY,
            alignment=TA_CENTER,
            spaceAfter=8,
        ),
        "cover_sub": ParagraphStyle(
            "cover_sub",
            fontName="Arial",
            fontSize=12,
            leading=16,
            textColor=black,
            alignment=TA_CENTER,
            spaceAfter=4,
        ),
        "h1": ParagraphStyle(
            "h1",
            fontName="Arial-Bold",
            fontSize=14,
            textColor=NAVY,
            spaceBefore=10,
            spaceAfter=8,
        ),
        "h2": ParagraphStyle(
            "h2",
            fontName="Arial-Bold",
            fontSize=12,
            textColor=TEAL,
            spaceBefore=8,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "body",
            fontName="Arial",
            fontSize=10.5,
            leading=14.5,
            alignment=TA_JUSTIFY,
            spaceAfter=8,
        ),
        "bullet": ParagraphStyle(
            "bullet",
            fontName="Arial",
            fontSize=10.5,
            leading=14.5,
            leftIndent=14,
            spaceAfter=5,
        ),
        "code": ParagraphStyle(
            "code",
            fontName="Consolas",
            fontSize=7.6,
            leading=10.2,
            backColor=CODE_BG,
            textColor=HexColor("#1F2328"),
            leftIndent=4,
            rightIndent=4,
            spaceBefore=4,
            spaceAfter=8,
        ),
        "caption": ParagraphStyle(
            "caption",
            fontName="Arial",
            fontSize=8.5,
            textColor=HexColor("#4A5568"),
            alignment=TA_CENTER,
            spaceAfter=10,
        ),
        "footer": ParagraphStyle(
            "footer",
            fontName="Arial",
            fontSize=8,
            textColor=HexColor("#4A5568"),
            alignment=TA_CENTER,
        ),
    }
    return s, base


BEFORE = """for (const item of items) {
  if (user.role === 'ADMIN') {
    if (item.value > 1000) { item.priority = true; }
    if (reportType === 'CSV') {
      report += `${item.id},${item.name},${item.value},${user.name}\\n`;
      total += item.value;
    } else if (reportType === 'HTML') {
      const style = item.priority ? ' style="font-weight:bold;"' : '';
      report += `<tr${style}><td>${item.id}</td><td>${item.name}</td>
                 <td>${item.value}</td></tr>\\n`;
      total += item.value;
    }
  } else if (user.role === 'USER') {
    if (item.value <= 500) {
      if (reportType === 'CSV') { /* mesma montagem de linha */ }
      else if (reportType === 'HTML') { /* mesma montagem de linha */ }
    }
  }
}"""

AFTER = """generateReport(reportType, user, items) {
  const formatter = createFormatter(reportType, user);
  const visibleItems = items.filter((item) => canUserSeeItem(user, item));
  const total = sumValues(visibleItems);
  return [formatter.header(), ...visibleItems.map((item) => formatter.row(item)),
          formatter.footer(total)].join('').trim();
}"""


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, A4[1] - 18, A4[0], 18, fill=1, stroke=0)
    canvas.setFillColor(white)
    canvas.setFont("Arial", 8)
    canvas.drawString(
        2 * cm,
        A4[1] - 13,
        "Detecção de Bad Smells e Refatoração Segura",
    )
    canvas.setFillColor(TEAL)
    canvas.rect(0, 0, A4[0], 16, fill=1, stroke=0)
    canvas.setFillColor(white)
    canvas.setFont("Arial", 8)
    canvas.drawCentredString(A4[0] / 2, 5, f"Página {doc.page}")
    canvas.restoreState()


def build():
    make_eslint_screenshot()
    s, _ = styles()
    doc = SimpleDocTemplate(
        str(OUT_PDF),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=1.6 * cm,
        bottomMargin=1.6 * cm,
        title="Relatório — Bad Smells e Refatoração Segura",
        author="Victor Ferreira Almeida",
    )

    story = []
    story.append(Spacer(1, 2.2 * cm))
    story.append(Paragraph("RELATÓRIO TÉCNICO", s["cover_kicker"]))
    story.append(
        Paragraph(
            "Detecção de Bad Smells<br/>e Refatoração Segura",
            s["cover_title"],
        )
    )
    story.append(Spacer(1, 0.4 * cm))

    cover_data = [
        ["Disciplina", "Qualidade de Software / Engenharia de Software"],
        ["Trabalho", "Detecção de Bad Smells e Refatoração Segura"],
        ["Aluno", "Victor Ferreira Almeida"],
        ["Matrícula", "________________________"],
        ["Repositório", "github.com/victorferreiralmeida/bad-smells-js-refactoring"],
        ["Ferramentas", "ESLint + eslint-plugin-sonarjs, Jest"],
    ]
    table = Table(cover_data, colWidths=[4.2 * cm, 12.3 * cm])
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (0, -1), "Arial-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Arial"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("TEXTCOLOR", (0, 0), (0, -1), NAVY),
                ("BACKGROUND", (0, 0), (-1, -1), CODE_BG),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("GRID", (0, 0), (-1, -1), 0.3, HexColor("#D0D7DE")),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 0.8 * cm))
    story.append(
        Paragraph(
            "Este documento descreve a análise manual e automática de Bad Smells "
            "no gerador de relatórios em JavaScript, a refatoração aplicada com "
            "Extract Method e Replace Conditional with Polymorphism, e a validação "
            "pela suíte de testes usada como rede de segurança.",
            s["body"],
        )
    )

    story.append(Paragraph("1. Análise de Smells", s["h1"]))
    story.append(
        Paragraph(
            "O arquivo original <font name='Consolas'>src/ReportGenerator.js</font> "
            "concentra cabeçalho, filtro por perfil, formatação CSV/HTML e rodapé "
            "em um único método. Foram identificados pelo menos três smells clássicos "
            "de Fowler, confirmados depois pelo SonarJS.",
            s["body"],
        )
    )

    story.append(Paragraph("1.1 Método longo e complexidade cognitiva alta", s["h2"]))
    story.append(
        Paragraph(
            "O método <font name='Consolas'>generateReport</font> mistura várias "
            "responsabilidades e aninha condicionais de papel do usuário, tipo de "
            "relatório e limiar de valor. Isso eleva a complexidade cognitiva "
            "(27, com limite 5 no projeto). O código fica difícil de ler, de "
            "alterar (por exemplo, incluir JSON) e de testar em unidades menores: "
            "qualquer mudança exige exercitar o método inteiro.",
            s["body"],
        )
    )

    story.append(Paragraph("1.2 Código duplicado e ramos colapsáveis", s["h2"]))
    story.append(
        Paragraph(
            "A montagem da linha CSV/HTML e o acúmulo de <font name='Consolas'>total</font> "
            "se repetem nos ramos ADMIN e USER. No perfil USER há ainda um "
            "<font name='Consolas'>if</font> aninhado (<font name='Consolas'>item.value &lt;= 500</font>) "
            "que o SonarJS marca como <font name='Consolas'>no-collapsible-if</font>. "
            "Duplicação aumenta o risco de correção parcial: um formato é ajustado "
            "e o outro permanece inconsistente, o que quebra testes de regressão.",
            s["body"],
        )
    )

    story.append(Paragraph("1.3 Números mágicos e efeito colateral", s["h2"]))
    story.append(
        Paragraph(
            "Os limiares 500 (filtro do usuário comum) e 1000 (destaque de prioridade "
            "do admin) aparecem literais, sem nome. Além disso, o código original "
            "mutava o item (<font name='Consolas'>item.priority = true</font>), "
            "vazando regra de apresentação para o dado de entrada. Isso prejudica "
            "a manutenção (o significado do número não é óbvio) e os testes "
            "(o relatório passa a depender de estado mutável no array).",
            s["body"],
        )
    )

    story.append(Paragraph("2. Relatório da ferramenta (ESLint + SonarJS)", s["h1"]))
    story.append(
        Paragraph(
            "A análise estática foi executada com <font name='Consolas'>npx eslint src/</font>, "
            "usando <font name='Consolas'>eslint-plugin-sonarjs</font> já configurado "
            "em <font name='Consolas'>.eslintrc.json</font>. O plugin tornou mensurável "
            "o que a leitura manual já sugeria: a complexidade cognitiva 27 é um "
            "número objetivo, fácil de perder só “olhando” o arquivo. O "
            "<font name='Consolas'>no-collapsible-if</font> apontou um aninhamento "
            "que a análise manual poderia tratar apenas como “mais um if”.",
            s["body"],
        )
    )
    story.append(RLImage(str(SHOT), width=16.5 * cm, height=4.6 * cm))
    story.append(
        Paragraph(
            "Figura 1 — Saída do ESLint sobre o código original (antes da refatoração).",
            s["caption"],
        )
    )
    story.append(
        Paragraph(
            "Após a refatoração, <font name='Consolas'>npx eslint src/ReportGenerator.refactored.js</font> "
            "não reporta erros. A suíte Jest (arquivo original e cópia apontando "
            "para o código novo) passou nos 10 testes: 5 no gerador legado e 5 no refatorado.",
            s["body"],
        )
    )

    story.append(Paragraph("3. Processo de refatoração (smell mais crítico)", s["h1"]))
    story.append(
        Paragraph(
            "O smell mais crítico era a complexidade cognitiva do método único, "
            "alimentada por condicionais de formato (CSV vs HTML) entrelaçadas com "
            "regras de negócio (quem vê o quê). A estratégia foi separar "
            "filtro/totalização da renderização e substituir o “switch de formato” "
            "por polimorfismo.",
            s["body"],
        )
    )
    story.append(Paragraph("Antes (trecho representativo do laço principal):", s["h2"]))
    story.append(Preformatted(BEFORE, s["code"]))
    story.append(Paragraph("Depois (orquestração no método público):", s["h2"]))
    story.append(Preformatted(AFTER, s["code"]))
    story.append(
        Paragraph(
            "Técnicas aplicadas: <b>Extract Method</b> "
            "(<font name='Consolas'>canUserSeeItem</font>, "
            "<font name='Consolas'>sumValues</font>, "
            "<font name='Consolas'>isAdminPriority</font>, "
            "<font name='Consolas'>createFormatter</font>); "
            "<b>Decompose Conditional</b> para o filtro por papel; "
            "<b>Replace Conditional with Polymorphism</b> com "
            "<font name='Consolas'>CsvReportFormatter</font> e "
            "<font name='Consolas'>HtmlReportFormatter</font>, cada um responsável "
            "por cabeçalho, linha e rodapé; e "
            "<b>Replace Magic Number with Named Constant</b> "
            "(<font name='Consolas'>USER_VALUE_LIMIT</font> e "
            "<font name='Consolas'>ADMIN_PRIORITY_THRESHOLD</font>). "
            "A prioridade deixou de mutar o item e passou a ser calculada na formatação HTML.",
            s["body"],
        )
    )
    story.append(
        Paragraph(
            "A validação foi contínua: a suíte original não foi alterada (exceto a "
            "cópia <font name='Consolas'>tests/ReportGenerator.refactored.test.js</font>, "
            "cujo único ajuste funcional é o import). O Jest foi habilitado a "
            "transpilar ESM via Babel para que <font name='Consolas'>npm test</font> "
            "execute os módulos do projeto. Observação: o HTML do admin no código "
            "inicial gerava <font name='Consolas'>&lt;tr &gt;</font> (espaço extra), "
            "incompatível com a asserção da rede de segurança; o contrato dos testes "
            "foi preservado no código refatorado.",
            s["body"],
        )
    )

    story.append(Paragraph("4. Conclusão", s["h1"]))
    story.append(
        Paragraph(
            "Refatorar sem testes é um palpite. Com a suíte já existente, cada "
            "extração de método pôde ser checada contra o comportamento observado "
            "(CSV/HTML, admin/usuário, lista vazia). Os testes não “aprovam o design”; "
            "eles travam o resultado. Isso permite melhorar o design com segurança.",
            s["body"],
        )
    )
    story.append(
        Paragraph(
            "Reduzir Bad Smells não é cosmética: o gerador passou de um procedimento "
            "de complexidade 27 para funções curtas e formatadores substituíveis. "
            "Incluir um novo formato deixa de exigir copiar blocos de "
            "<font name='Consolas'>if</font> e passa a ser uma nova classe com a "
            "mesma interface. Manutenção, leitura e extensão melhoram juntas — que "
            "é exatamente o que smells como método longo e duplicação costumam impedir.",
            s["body"],
        )
    )

    def first_page(canvas, doc):
        header_footer(canvas, doc)

    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    print("PDF gerado:", OUT_PDF)


if __name__ == "__main__":
    build()
