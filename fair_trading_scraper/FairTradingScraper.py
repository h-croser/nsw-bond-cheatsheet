import re
from datetime import datetime
from io import BytesIO

import requests
from pandas import ExcelFile, DataFrame, concat, Series
from requests import Response
from bs4 import BeautifulSoup, ResultSet
from tqdm import tqdm


class FairTradingScraper:
    DATA_LIST_URL: str = "https://www.fairtrading.nsw.gov.au/about-fair-trading/rental-bond-data"
    DATA_LINK_PREFIX: str = "https://www.fairtrading.nsw.gov.au/__data/assets/excel_doc/"

    @staticmethod
    def _get_links_from_table(grandparent_id: str, parent_tag: str) -> list[str]:
        response: Response = requests.get(FairTradingScraper.DATA_LIST_URL)
        soup = BeautifulSoup(response.text, "html.parser")

        link_tags: ResultSet = soup.find(id=grandparent_id).find('div').find(parent_tag).find_all('a')
        links: list[str] = [a_tag.get('href') for a_tag in link_tags]
        url_pattern = re.compile(f'{FairTradingScraper.DATA_LINK_PREFIX}(?!.*year).*', flags=re.I)
        matching_links: list[str] = [link for link in links if re.match(url_pattern, link)]

        return matching_links

    @staticmethod
    def _get_excel_file(file_link: str) -> ExcelFile:
        response = requests.get(file_link)
        file_object = BytesIO(response.content)
        return ExcelFile(file_object, engine='openpyxl')

    @staticmethod
    def _get_df_from_links(links: list[str], links_name: str) -> DataFrame:
        complete_df: DataFrame = DataFrame()
        for link in tqdm(links, desc=f"Loading {links_name}", unit="links"):
            excel_file: ExcelFile = FairTradingScraper._get_excel_file(link)
            data_df: DataFrame = excel_file.parse(skiprows=2)
            complete_df = concat([complete_df, data_df], ignore_index=True)

        return complete_df

    @staticmethod
    def get_lodgement_dataframe() -> DataFrame:
        lodgement_links: list[str] = FairTradingScraper._get_links_from_table('panel1', 'table')

        lodgement_df: DataFrame = FairTradingScraper._get_df_from_links(lodgement_links, "lodgements")
        column_replace = {
            'Lodgement Date': 'date_lodged',
            'Postcode': 'postcode',
            'Dwelling Type': 'dwelling_type',
            'Bedrooms': 'num_bedrooms',
            'Weekly Rent': 'weekly_rent'
        }
        lodgement_df = lodgement_df.rename(columns=column_replace)

        return lodgement_df

    @staticmethod
    def get_refunds_dataframe() -> DataFrame:
        refunds_links: list[str] = FairTradingScraper._get_links_from_table('panel2', 'table')

        refunds_df = FairTradingScraper._get_df_from_links(refunds_links, "refunds")
        column_replace = {
            'Payment Date': 'date_paid',
            'Postcode': 'postcode',
            'Dwelling Type': 'dwelling_type',
            'Bedrooms': 'num_bedrooms',
            'Payment To Agent': 'agent_payment',
            'Payment To Tenant': 'tenant_payment',
            'Days Bond Held': 'num_days_held'
        }
        refunds_df = refunds_df.rename(columns=column_replace)

        return refunds_df

    @staticmethod
    def get_holdings_dataframe() -> DataFrame:
        holdings_links: list[str] = FairTradingScraper._get_links_from_table('panel3', 'ul')
        month_pattern = re.compile(r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s*\d{4}\b', flags=re.I)

        complete_df: DataFrame = DataFrame()
        for link in tqdm(holdings_links, desc="Loading holdings", unit="links"):
            excel_file: ExcelFile = FairTradingScraper._get_excel_file(link)
            header_df: DataFrame = excel_file.parse(nrows=1, header=None)
            header_str = str(header_df.iloc[0, 0])
            month_match = re.search(month_pattern, header_str)
            month_str = ''
            if month_match:
                month_str = month_match.group(0)

            data_df: DataFrame = excel_file.parse(skiprows=2)
            data_df['month'] = month_str
            complete_df = concat([complete_df, data_df], ignore_index=True)

        column_replace = {
            'Postcode': 'postcode',
            'Bonds Held': 'bonds_held'
        }
        complete_df = complete_df.rename(columns=column_replace)

        return complete_df

    @staticmethod
    def update_holdings():
        holdings_df: DataFrame = FairTradingScraper.get_holdings_dataframe()
        holdings_df.to_csv('./holdings.csv', index=False)

    @staticmethod
    def update_lodgements():
        def read_row(row: Series):
            try:
                row['num_bedrooms'] = int(row['num_bedrooms'])
            except ValueError:
                row['num_bedrooms'] = -1
            try:
                row['weekly_rent'] = int(row['weekly_rent'])
            except ValueError:
                row['weekly_rent'] = -1
            try:
                row['date_lodged'] = datetime.fromisoformat(str(row['date_lodged'])).date()
            except ValueError:
                row['date_lodged'] = datetime.fromtimestamp(0).date()

            return row

        lodgements_df: DataFrame = FairTradingScraper.get_lodgement_dataframe()
        lodgements_df = lodgements_df.apply(read_row, axis=1)
        lodgements_df.to_csv('./lodgements.csv', index=False)

    @staticmethod
    def update_refunds():
        def read_row(row: Series):
            try:
                row['num_bedrooms'] = int(row['num_bedrooms'])
            except ValueError:
                row['num_bedrooms'] = -1
            try:
                row['agent_payment'] = int(row['agent_payment'])
            except ValueError:
                row['agent_payment'] = -1
            try:
                row['tenant_payment'] = int(row['tenant_payment'])
            except ValueError:
                row['tenant_payment'] = -1
            try:
                row['num_days_held'] = int(row['num_days_held'])
            except ValueError:
                row['num_days_held'] = -1
            try:
                row['date_paid'] = datetime.fromisoformat(str(row['date_paid'])).date()
            except ValueError:
                row['date_paid'] = datetime.fromtimestamp(0).date()

            return row

        refunds_df: DataFrame = FairTradingScraper.get_refunds_dataframe()
        refunds_df = refunds_df.apply(read_row, axis=1)
        refunds_df.to_csv('./refunds.csv', index=False)

    @staticmethod
    def update_all():
        print("Updating models...")
        FairTradingScraper.update_holdings()
        FairTradingScraper.update_lodgements()
        FairTradingScraper.update_refunds()
        print("All models updated")


if __name__ == "__main__":
    FairTradingScraper.update_all()
