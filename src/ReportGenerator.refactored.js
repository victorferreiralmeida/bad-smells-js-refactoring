const USER_VALUE_LIMIT = 500;
const ADMIN_PRIORITY_THRESHOLD = 1000;

export class ReportGenerator {
  constructor(database) {
    this.db = database;
  }

  /**
   * Gera um relatório de itens baseado no tipo e no usuário.
   * - Admins veem tudo.
   * - Users comuns só veem itens com valor <= USER_VALUE_LIMIT.
   */
  generateReport(reportType, user, items) {
    const formatter = createFormatter(reportType, user);
    const visibleItems = items.filter((item) => canUserSeeItem(user, item));
    const total = sumValues(visibleItems);

    return [
      formatter.header(),
      ...visibleItems.map((item) => formatter.row(item)),
      formatter.footer(total),
    ]
      .join('')
      .trim();
  }
}

function canUserSeeItem(user, item) {
  if (user.role === 'ADMIN') {
    return true;
  }

  if (user.role === 'USER') {
    return item.value <= USER_VALUE_LIMIT;
  }

  return false;
}

function sumValues(items) {
  return items.reduce((total, item) => total + item.value, 0);
}

function isAdminPriority(user, item) {
  return user.role === 'ADMIN' && item.value > ADMIN_PRIORITY_THRESHOLD;
}

function createFormatter(reportType, user) {
  if (reportType === 'CSV') {
    return new CsvReportFormatter(user);
  }

  if (reportType === 'HTML') {
    return new HtmlReportFormatter(user);
  }

  return new EmptyReportFormatter();
}

class CsvReportFormatter {
  constructor(user) {
    this.user = user;
  }

  header() {
    return 'ID,NOME,VALOR,USUARIO\n';
  }

  row(item) {
    return `${item.id},${item.name},${item.value},${this.user.name}\n`;
  }

  footer(total) {
    return `\nTotal,,\n${total},,\n`;
  }
}

class HtmlReportFormatter {
  constructor(user) {
    this.user = user;
  }

  header() {
    return [
      '<html><body>\n',
      '<h1>Relatório</h1>\n',
      `<h2>Usuário: ${this.user.name}</h2>\n`,
      '<table>\n',
      '<tr><th>ID</th><th>Nome</th><th>Valor</th></tr>\n',
    ].join('');
  }

  row(item) {
    const style = isAdminPriority(this.user, item)
      ? ' style="font-weight:bold;"'
      : '';

    return `<tr${style}><td>${item.id}</td><td>${item.name}</td><td>${item.value}</td></tr>\n`;
  }

  footer(total) {
    return `</table>\n<h3>Total: ${total}</h3>\n</body></html>\n`;
  }
}

class EmptyReportFormatter {
  header() {
    return '';
  }

  row() {
    return '';
  }

  footer() {
    return '';
  }
}
