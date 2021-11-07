# -*- coding: utf-8 -*-
import click
import logging
from pathlib import Path
from ground_data_preprocess import GroundDataProcessor
from aerial_data_preprocess import AerialDataProcessor
from dotenv import find_dotenv, load_dotenv


@click.command()
@click.argument('input_filepath', type=click.Path(exists=True))
@click.argument('output_filepath', type=click.Path())
def main(input_filepath, output_filepath):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info('making final data set from raw data')
    gpreprocessor = GroundDataProcessor()
    apreprocessor = AerialDataProcessor()

    logger.info('reading data')
    gpreprocessor.read_data(input_filepath)
    apreprocessor.read_data('data/raw/raw_forest_aerial_data.csv')

    logger.info('processing data')
    gpreprocessor.process_data()
    apreprocessor.process_data()
    

    logger.info('saving processed data')
    gpreprocessor.write_data(output_filepath)
    apreprocessor.write_data('data/processed/')


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
