import re
from datetime import datetime
from io import BytesIO
from os import makedirs
from os.path import dirname, abspath, join
from typing import Optional

import requests
from pandas import ExcelFile, DataFrame, concat, Series, cut
from requests import Response
from bs4 import BeautifulSoup, ResultSet
from tqdm import tqdm

CACHE_DIR: str = join(dirname(abspath(__file__)), "fair_trading_cache")
CACHE_MAP_RECORD: str = join(CACHE_DIR, "cache_map.txt")


class FileCache:
    @staticmethod
    def build_cache_map() -> dict[str, str]:
        cache_map: dict[str, str] = {}
        makedirs(CACHE_DIR, exist_ok=True)
        cache_map_file: str = CACHE_MAP_RECORD
        try:
            open(cache_map_file)
        except FileNotFoundError:
            open(cache_map_file, 'x')
        with open(cache_map_file) as f:
            lines = f.readlines()
        for line in lines:
            line_split = line.split(' ')
            if len(line_split) < 2:
                continue
            filename = line_split[0]
            file_url = ' '.join(line_split[1:]).strip('\n')
            cache_map[file_url] = filename
        return cache_map

    @staticmethod
    def get_filename(file_url: str) -> Optional[str]:
        filename: Optional[str] = FileCache.CACHE_MAP.get(file_url)
        if filename is None:
            return None
        filepath: str = join(CACHE_DIR, filename)
        return filepath

    @staticmethod
    def set_filename_map(file_url: str, ext: str) -> str:
        filename: str = str(abs(hash(file_url))) + f'.{ext}'
        while filename in FileCache.CACHE_MAP:
            filename = str(abs(hash(filename))) + f'.{ext}'
        FileCache.CACHE_MAP[file_url] = filename

        cache_map_file: str = CACHE_MAP_RECORD
        with open(cache_map_file, 'a') as f:
            f.write(f'{filename} {file_url}\n')

        return filename

    CACHE_MAP: dict[str, str] = build_cache_map()


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
    def _get_excel_file(file_url: str) -> ExcelFile:
        filename: Optional[str] = FileCache.get_filename(file_url)
        if filename is None:
            filename = FileCache.set_filename_map(file_url, 'xlsx')
            filepath: str = join(CACHE_DIR, filename)
            response = requests.get(file_url)
            file_object = BytesIO(response.content)
            with open(filepath, 'wb') as f:
                f.write(file_object.getvalue())
        else:
            filepath: str = join(CACHE_DIR, filename)
            with open(filepath, 'rb') as f:
                file_object = BytesIO(f.read())
        excel_file = ExcelFile(file_object, engine='openpyxl')

        return excel_file

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
            if month_match is None:
                continue
            date_str = month_match.group(0)
            date_obj = datetime.strptime(date_str, "%B %Y")

            data_df: DataFrame = excel_file.parse(skiprows=2)
            data_df['date'] = date_obj
            complete_df = concat([complete_df, data_df], ignore_index=True)

        complete_df = complete_df.rename(columns={'Postcode': 'postcode', 'Bonds Held': 'bonds_held'})
        complete_df = complete_df[['postcode', 'bonds_held', 'date']]

        return complete_df

    @staticmethod
    def update_holdings(holdings_df: DataFrame):
        holdings_df.to_csv('./holdings.csv', index=False)

    @staticmethod
    def update_lodgements(lodgements_df: DataFrame):
        def read_row(row: Series):
            try:
                row['num_bedrooms'] = int(row['num_bedrooms'])
            except ValueError:
                return
            try:
                row['weekly_rent'] = int(row['weekly_rent'])
            except ValueError:
                return
            try:
                row['date_lodged'] = datetime.fromisoformat(str(row['date_lodged'])).date()
            except ValueError:
                return

            return row

        lodgements_df = lodgements_df.apply(read_row, axis=1)
        lodgements_df = lodgements_df[['date_lodged', 'postcode', 'num_bedrooms', 'weekly_rent']]
        lodgements_df = lodgements_df.dropna()
        lodgements_df = lodgements_df.astype({'postcode': int, 'num_bedrooms': int, 'weekly_rent': int})
        # lodgements_df['average_rent'] = lodgements_df.groupby(['date_lodged', 'postcode'])['weekly_rent'].transform('mean')
        # lodgements_df = lodgements_df[['date_lodged', 'postcode', 'num_bedrooms', 'average_rent']].drop_duplicates(['date_lodged', 'postcode'])
        lodgements_df = lodgements_df[['date_lodged', 'postcode', 'num_bedrooms', 'weekly_rent']]

        lodgements_df.to_csv('./lodgements.csv', index=False)

    @staticmethod
    def update_refunds_optimised(refunds_df: DataFrame):
        refunds_df = refunds_df[['date_paid', 'tenant_payment', 'agent_payment', 'postcode']]
        refunds_df = refunds_df.groupby(['date_paid', 'postcode']).agg({'tenant_payment': 'sum', 'agent_payment': 'sum'}).reset_index()
        refunds_df.to_csv('./refunds-optimised.csv', index=False)

    @staticmethod
    def update_refunds_totals(refunds_df: DataFrame):
        refunds_df = refunds_df[['tenant_payment', 'agent_payment', 'postcode']]
        refunds_df = refunds_df.groupby(['postcode']).agg({'tenant_payment': 'sum', 'agent_payment': 'sum'}).reset_index()
        refunds_df.to_csv('./refunds-totals.csv', index=False)

    @staticmethod
    def update_refunds_recipients(refunds_df: DataFrame):
        portions_df = refunds_df.loc[:, ['tenant_payment', 'agent_payment', 'postcode']]
        portions_df.loc[:, 'landlord_portion_prebin'] = portions_df['agent_payment'] / (portions_df['agent_payment'] + portions_df['tenant_payment'])
        portions_df.loc[:, 'landlord_portion_binned'] = cut(portions_df['landlord_portion_prebin'], bins=3, labels=False, include_lowest=True)
        portions_df.loc[:, 'recipient'] = portions_df.loc[:, 'landlord_portion_binned'].map({0: 'Tenant', 1: 'Split', 2: 'Landlord'})
        portions_df['bin_count'] = portions_df.groupby(['postcode', 'recipient']).transform('count')
        portions_df.drop_duplicates(subset=['postcode', 'recipient'], inplace=True)
        portions_df = portions_df.loc[:, ['postcode', 'recipient', 'bin_count']]
        portions_df = portions_df.dropna()
        portions_df.to_csv('./refunds-portions.csv', index=False)

    @staticmethod
    def update_all():
        print("Gathering models")
        # holdings_df: DataFrame = FairTradingScraper.get_holdings_dataframe()
        lodgements_df: DataFrame = FairTradingScraper.get_lodgement_dataframe()
        # refunds_df: DataFrame = FairTradingScraper.get_refunds_dataframe()
        print("Updating models...")
        # FairTradingScraper.update_holdings(holdings_df)
        FairTradingScraper.update_lodgements(lodgements_df)
        # FairTradingScraper.update_refunds_optimised(refunds_df)
        # FairTradingScraper.update_refunds_totals(refunds_df)
        # FairTradingScraper.update_refunds_recipients(refunds_df)
        print("All models updated")


if __name__ == "__main__":
    FairTradingScraper.update_all()
