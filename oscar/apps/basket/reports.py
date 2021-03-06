import csv

from django.db.models import get_model

from oscar.core.loading import get_class, get_classes
ReportGenerator = get_class('dashboard.reports.reports', 'ReportGenerator')
ReportCSVFormatter = get_class('dashboard.reports.reports', 'ReportCSVFormatter')
ReportHTMLFormatter = get_class('dashboard.reports.reports', 'ReportHTMLFormatter')
Basket = get_model('basket', 'Basket')
OPEN, SUBMITTED = get_classes('basket.models', ['OPEN', 'SUBMITTED'])


class OpenBasketReportCSVFormatter(ReportCSVFormatter):
    filename_template = 'open-baskets-%s-%s.csv'

    def generate_csv(self, response, baskets):
        writer = csv.writer(response)
        header_row = ['User ID',
                      'Name',
                      'Email',
                      'Basket status',
                      'Num lines',
                      'Num items',
                      'Value',
                      'Date of creation',
                      'Time since creation',
                     ]
        writer.writerow(header_row)

        for basket in baskets:
            if basket.owner:
                row = [basket.owner_id, basket.owner.get_full_name(), basket.owner.email,
                       basket.status, basket.num_lines,
                       basket.num_items, basket.total_incl_tax,
                       self.format_datetime(basket.date_created),
                       basket.time_since_creation]
            else:
                row = [basket.owner_id, None, None, basket.status, basket.num_lines,
                       basket.num_items, basket.total_incl_tax,
                       self.format_datetime(basket.date_created), basket.time_since_creation]
            writer.writerow(row)

    def filename(self, **kwargs):
        return self.filename_template % (kwargs['start_date'], kwargs['end_date'])


class OpenBasketReportHTMLFormatter(ReportHTMLFormatter):
    filename_template = 'dashboard/reports/partials/open_basket_report.html'


class OpenBasketReportGenerator(ReportGenerator):
    """
    Report of baskets which haven't been submitted yet
    """
    code = 'open_baskets'
    description = 'Open baskets'

    formatters = {
        'CSV_formatter': OpenBasketReportCSVFormatter,
        'HTML_formatter': OpenBasketReportHTMLFormatter
    }

    def generate(self):
        additional_data = {
            'start_date': self.start_date,
            'end_date': self.end_date
        }
        baskets = Basket._default_manager.filter(status=OPEN)
        return self.formatter.generate_response(baskets, **additional_data)


class SubmittedBasketReportCSVFormatter(ReportCSVFormatter):
    filename_template = 'submitted_baskets-%s-%s.csv'

    def generate_csv(self, response, baskets):
        writer = csv.writer(response)
        header_row = ['User ID',
                      'User',
                      'Basket status',
                      'Num lines',
                      'Num items',
                      'Value',
                      'Date created',
                      'Time between creation and submission',
                     ]
        writer.writerow(header_row)

        for basket in baskets:
            row = [basket.owner_id,
                   basket.owner,
                   basket.status,
                   basket.num_lines,
                   basket.num_items,
                   basket.total_incl_tax,
                   self.format_datetime(basket.date_created),
                   basket.time_before_submit]
            writer.writerow(row)

    def filename(self, **kwargs):
        return self.filename_template % (kwargs['start_date'], kwargs['end_date'])


class SubmittedBasketReportHTMLFormatter(ReportHTMLFormatter):
    filename_template = 'dashboard/reports/partials/submitted_basket_report.html'


class SubmittedBasketReportGenerator(ReportGenerator):
    """
    Report of baskets that have been submitted
    """
    code = 'submitted_baskets'
    description = 'Submitted baskets'

    formatters = {
        'CSV_formatter': SubmittedBasketReportCSVFormatter,
        'HTML_formatter': SubmittedBasketReportHTMLFormatter
    }

    def generate(self):
        additional_data = {
            'start_date': self.start_date,
            'end_date': self.end_date
        }
        baskets = Basket._default_manager.filter(status=SUBMITTED)
        return self.formatter.generate_response(baskets, **additional_data)
