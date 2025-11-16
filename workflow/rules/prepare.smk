"""Rules in this file focus on parsing and cleaning data."""

rule prepare_population:
    message:
        "{wildcards.shape}: preparing population raster."
    input:
        raster=rules.unzip_GHSL.output[0],
        like_vector="resources/user/{shape}/shapes.parquet",
    output:
        path="resources/automatic/shapes/{shape}/population.tif",
    log:
        "logs/{shape}/prepare_population.log"
    wrapper:
        "v7.9.0/geo/rasterio/clip"


rule prepare_shapes:
    message:
        "{wildcards.shape}: preparing polygons for European industry disaggregation."
    input:
        shapes="resources/user/{shape}/shapes.parquet",
        population=rules.prepare_population.output.path
    output:
        shapes="resources/automatic/shapes/{shape}/shapes.parquet"
    log:
        "logs/{shape}/prepare_shapes.log"
    conda:
        "../envs/prepare.yaml"
    script:
        "../scripts/prepare_shapes.py"


rule prepare_ammonia_production:
    message:
        "Preparing Global ammonia production statistics."
    input:
        usgs=rules.download_ammonia_usgs.output.file,
    output:
        production="resources/automatic/ammonia/production.csv",
    log:
        "logs/prepare/prepare_ammonia_production.log"
    conda:
        "../envs/prepare.yaml"
    script:
        "../scripts/prepare_ammonia_production.py"


rule prepare_coke_transformation:
    message:
        "Preparing coke transformation data."
    input:
        eurostat_dir="resources/automatic/eurostat",
    output:
        coke="resources/automatic/prepare/coke/transformation.csv"
    log:
        "logs/prepare/prepare_coke_transformation.log"
    conda:
        "../envs/prepare.yaml"
    script:
        "../scripts/prepare_coke_transformation.py"


rule prepare_current_europe_production:
    message:
        "Preparing current European production."
    params:
        industry=config["industry"],
    input:
        ch_industrial_production=rules.download_CHE_industry.output.file,
        ammonia_production=rules.prepare_ammonia_production.output.production,
        jrc_dir="resources/automatic/jrc_idees/",
        eurostat_dir="resources/automatic/eurostat/",
    output:
        production="resources/automatic/europe/current_production.csv",
    log:
        "logs/prepare/prepare_current_europe_production.log",
    conda:
        "../envs/prepare.yaml"
    script:
        "../scripts/prepare_current_europe_production.py"


rule prepare_future_europe_production:
    message:
        "{wildcards.year}: preparing future European production."
    params:
        industry=config["industry"],
    input:
        current=rules.prepare_current_europe_production.output.production,
    output:
        production="resources/automatic/europe/{year}/production.csv",
    log:
        "logs/{year}/prepare_future_europe_production.log",
    conda:
        "../envs/prepare.yaml",
    script:
        "../scripts/prepare_future_europe_production.py"


rule prepare_current_europe_energy_demand:
    params:
        industry=config["industry"],
        ammonia=config["ammonia"],
    input:
        transformation_output_coke=rules.prepare_coke_transformation.output.coke,
        jrc="resources/automatic/jrc_idees",
        industrial_production_per_country=rules.prepare_current_europe_production.output.production,
    output:
        energy_demand="resources/automatic/europe/current_energy_demand.csv"
    log:
        "logs/prepare/prepare_current_europe_energy_demand.log"
    conda:
        "../envs/prepare.yaml"
    script:
        "../scripts/prepare_current_europe_energy_demand.py"


# TODO: rename to rates
rule prepare_sector_ratios:
    params:
        industry=config["industry"],
        ammonia=config["ammonia"],
    input:
        ammonia_production=rules.prepare_ammonia_production.output.production,
        idees="resources/automatic/jrc_idees",
    output:
        industry_sector_ratios="resources/automatic/prepare/sector_ratios.csv",
    log:
        "logs/prepare/prepare_sector_ratios.log",
    conda:
        "../envs/prepare.yaml"
    script:
        "../scripts/prepare_sector_ratios.py"


# TODO: rename to subsector ratios per country or something similar.
rule prepare_sector_ratios_intermediate:
    params:
        industry=config["industry"],
    input:
        industry_sector_ratios=rules.prepare_sector_ratios.output.industry_sector_ratios,
        industrial_energy_demand_per_country_today=rules.prepare_current_europe_energy_demand.output.energy_demand,
        industrial_production_per_country=rules.prepare_future_europe_production.output.production,
    output:
        industry_sector_ratios="resources/automatic/prepare/sector_ratios_intermediate_{year}.csv",
    log:
         "logs/prepare/prepare_sector_ratios_intermediate_{year}.log"
    conda:
        "../envs/prepare.yaml"
    script:
        "../scripts/prepare_sector_ratios_intermediate.py"
