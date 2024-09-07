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

BASE_DATA_DIR = join(dirname(dirname(abspath(__file__))), 'src', 'data')


class FileCache:
    @staticmethod
    def build_cache_map() -> dict[str, str]:
        cache_map: dict[str, str] = {}
        makedirs(CACHE_DIR, exist_ok=True)
        cache_map_file: str = CACHE_MAP_RECORD
        try:
            open(cache_map_file)
            print("Fair Trading cache found")
        except FileNotFoundError:
            print("No Fair Trading cache found")
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
    DATA_ROOT_PATH: str = "https://www.nsw.gov.au"
    DATA_LIST_URL: str = DATA_ROOT_PATH + "/housing-and-construction/rental-forms-surveys-and-data/rental-bond-data"
    DATA_LINK_PREFIX: str = "/sites/default/files/"

    @staticmethod
    def _get_links_from_table(search_term: str) -> list[str]:
        response: Response = requests.get(FairTradingScraper.DATA_LIST_URL)
        soup = BeautifulSoup(response.text, "html.parser")
        url_pattern = re.compile(f'{FairTradingScraper.DATA_LINK_PREFIX}.*{search_term}((?!year).)*\.xlsx', flags=re.I)

        link_tags: ResultSet = soup.find_all('a', href=True, recursive=True)
        matching_links: list[str] = []
        for a_tag in link_tags:
            if url_pattern.search(a_tag['href']):
                link = a_tag['href']
                if not link.startswith(FairTradingScraper.DATA_ROOT_PATH):
                    link = FairTradingScraper.DATA_ROOT_PATH + link
                matching_links.append(link)

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
        lodgement_links: list[str] = FairTradingScraper._get_links_from_table('lodgement')

        lodgement_df: DataFrame = FairTradingScraper._get_df_from_links(lodgement_links, "lodgements")
        column_replace = {
            'Lodgement Date': 'date',
            'Postcode': 'postcode',
            'Dwelling Type': 'dwelling_type',
            'Bedrooms': 'num_bedrooms',
            'Weekly Rent': 'weekly_rent'
        }
        lodgement_df = lodgement_df.rename(columns=column_replace)

        return lodgement_df

    @staticmethod
    def get_refunds_dataframe() -> DataFrame:
        refunds_links: list[str] = FairTradingScraper._get_links_from_table('refund')

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
        holdings_links: list[str] = FairTradingScraper._get_links_from_table('held')
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
        holdings_df.to_csv(join(BASE_DATA_DIR, 'holdings.csv'), index=False)
        holdings_df.to_parquet(join(BASE_DATA_DIR, 'holdings.parquet'), index=False)

    @staticmethod
    def update_rents(lodgements_df: DataFrame):
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
                row['date'] = str(row['date'])[:8] + '01'
            except (ValueError, IndexError):
                return

            return row

        lodgements_df = lodgements_df.apply(read_row, axis=1)
        lodgements_df = lodgements_df.dropna()
        lodgements_df = lodgements_df.astype({'date': str, 'postcode': int, 'weekly_rent': int, 'num_bedrooms': int})
        lodgements_df = lodgements_df[['date', 'postcode', 'weekly_rent', 'num_bedrooms']]

        postcode_median_rents_df: DataFrame = lodgements_df.groupby(['date', 'postcode']).agg(
            median_rent=('weekly_rent', 'median'),
            data_points=('weekly_rent', 'size')
        ).reset_index()
        all_postcodes_median_rents_df: DataFrame = lodgements_df.groupby('date').agg(
            median_rent=('weekly_rent', 'median'),
            data_points=('weekly_rent', 'size')
        ).reset_index()
        all_postcodes_median_rents_df['postcode'] = 0
        median_rents_df: DataFrame = concat([postcode_median_rents_df, all_postcodes_median_rents_df], ignore_index=True)

        postcode_bedrooms_median_rents_df: DataFrame = lodgements_df.groupby(['date', 'postcode', 'num_bedrooms']).agg(
            median_rent=('weekly_rent', 'median'),
            data_points=('weekly_rent', 'size')
        ).reset_index()
        all_postcodes_bedrooms_median_rents_df: DataFrame = lodgements_df.groupby(['date', 'num_bedrooms']).agg(
            median_rent=('weekly_rent', 'median'),
            data_points=('weekly_rent', 'size')
        ).reset_index()
        all_postcodes_bedrooms_median_rents_df['postcode'] = 0
        bedrooms_median_rents_df: DataFrame = concat([postcode_bedrooms_median_rents_df, all_postcodes_bedrooms_median_rents_df], ignore_index=True)

        median_rents_df.to_csv(join(BASE_DATA_DIR, 'median-rents.csv'), index=False)
        median_rents_df.to_parquet(join(BASE_DATA_DIR, 'median-rents.parquet'), index=False)
        bedrooms_median_rents_df.to_csv(join(BASE_DATA_DIR, 'median-rents-bedrooms.csv'), index=False)
        bedrooms_median_rents_df.to_parquet(join(BASE_DATA_DIR, 'median-rents-bedrooms.parquet'), index=False)

    @staticmethod
    def update_refunds_totals(refunds_df: DataFrame):
        refunds_df = refunds_df[['tenant_payment', 'agent_payment', 'postcode']]
        refunds_df = refunds_df.groupby(['postcode']).agg({'tenant_payment': 'sum', 'agent_payment': 'sum'}).reset_index()
        refunds_df.to_csv(join(BASE_DATA_DIR, 'refunds-totals.csv'), index=False)
        refunds_df.to_parquet(join(BASE_DATA_DIR, 'refunds-totals.parquet'), index=False)

    @staticmethod
    def update_refunds_recipients(refunds_df: DataFrame):
        portions_df = refunds_df.loc[:, ['tenant_payment', 'agent_payment', 'postcode']]
        portions_df.loc[:, 'landlord_portion_prebin'] = portions_df['agent_payment'] / (portions_df['agent_payment'] + portions_df['tenant_payment'])
        portions_df.loc[:, 'landlord_portion_binned'] = cut(portions_df['landlord_portion_prebin'], bins=3, labels=False, include_lowest=True)
        portions_df.loc[:, 'recipient'] = portions_df.loc[:, 'landlord_portion_binned'].map({0: 'Tenant', 1: 'Split', 2: 'Landlord'})
        portions_df['bin_count'] = portions_df.groupby(['postcode', 'recipient'])['postcode'].transform('count')
        portions_df.drop_duplicates(subset=['postcode', 'recipient'], inplace=True)
        portions_df = portions_df.loc[:, ['postcode', 'recipient', 'bin_count']]
        portions_df = portions_df.dropna()
        portions_df.to_csv(join(BASE_DATA_DIR, 'refunds-portions.csv'), index=False)
        portions_df.to_parquet(join(BASE_DATA_DIR, 'refunds-portions.parquet'), index=False)

    @staticmethod
    def update_all():
        print("Gathering models")
        holdings_df: DataFrame = FairTradingScraper.get_holdings_dataframe()
        refunds_df: DataFrame = FairTradingScraper.get_refunds_dataframe()
        lodgements_df: DataFrame = FairTradingScraper.get_lodgement_dataframe()
        print("Updating models...")
        FairTradingScraper.update_holdings(holdings_df)
        FairTradingScraper.update_refunds_totals(refunds_df)
        FairTradingScraper.update_refunds_recipients(refunds_df)
        FairTradingScraper.update_rents(lodgements_df)
        print("All models updated")


if __name__ == "__main__":
    FairTradingScraper.update_all()
