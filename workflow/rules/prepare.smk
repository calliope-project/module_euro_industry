"""Rules in this file focus on parsing and cleaning data."""

rule prepare_population_raster:
    input:
        raster=rules.unzip_GHSL.output[0],
        like_vector="resources/user/{shape}/shapes.parquet",
    output:
        path="resources/automatic/shapes/{shape}/population.tif",
    log:
        "logs/prepare/prepare_population_raster_{shape}.log"
    wrapper:
        "v7.9.0/geo/rasterio/clip"


rule prepare_shapes:
    message:
        "Preparing input {wildcards.shape} polygons for European Industry processing."
    input:
        shapes="resources/user/{shape}/shapes.parquet",
        population=rules.prepare_population_raster.output.path
    output:
        filtered="resources/automatic/shapes/{shape}/shapes.parquet"
    log:
        "logs/prepare/prepare_shapes_{shape}.log"
    conda:
        "../envs/prepare.yaml"
    script:
        "../scripts/prepare_shapes.py"


rule prepare_ammonia_production:
    input:
        usgs=rules.download_ammonia_usgs.output.file,
    output:
        prepared="resources/automatic/prepare/ammonia_production.csv",
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
        coke="resources/automatic/prepare/coke_transformation.csv"
    log:
        "logs/prepare/prepare_coke_transformation.log"
    conda:
        "../envs/prepare.yaml"
    script:
        "../scripts/prepare_coke_transformation.py"


rule prepare_current_aggregated_production:  # TODO: change to national production
    params:
        industry=config["industry"],
    input:
        ch_industrial_production=rules.download_CHE_industry.output.file,
        ammonia_production=rules.prepare_ammonia_production.output.prepared,
        jrc_dir="resources/automatic/jrc_idees/",
        eurostat_dir="resources/automatic/eurostat/",
    output:
        production_per_country="resources/automatic/prepare/current_national_production.csv",
    log:
        "logs/prepare/current_aggregated_production.log",
    conda:
        "../envs/prepare.yaml"
    script:
        "../scripts/prepare_current_aggregated_production.py"


rule prepare_future_aggregated_production:
    params:
        industry=config["industry"],
    input:
        current=rules.prepare_current_aggregated_production.output.production_per_country,
    output:
        future="results/aggregated/future_production_{year}.csv",
    log:
        "logs/prepare/future_aggregated_production_{year}.log",
    conda:
        "../envs/prepare.yaml",
    script:
        "../scripts/prepare_future_aggregated_production.py"


rule prepare_current_energy_demand_per_country:
    params:
        countries=config["countries"],
        industry=config["industry"],
        ammonia=config["ammonia"],
    input:
        transformation_output_coke=rules.prepare_coke_transformation.output.coke,
        jrc="resources/automatic/jrc_idees",
        industrial_production_per_country=rules.prepare_current_aggregated_production.output.production_per_country,
    output:
        current_energy_demand="results/aggregated/current_industrial_energy_demand_per_country.csv"
    log:
        "logs/prepare/prepare_current_industrial_energy_demand_per_country.log"
    conda:
        "../envs/prepare.yaml"
    script:
        "../scripts/prepare_current_energy_demand_per_country.py"


rule prepare_sector_ratios:
    params:
        industry=config["industry"],
        ammonia=config["ammonia"],
    input:
        ammonia_production=rules.prepare_ammonia_production.output.prepared,
        idees="resources/automatic/jrc_idees",
    output:
        industry_sector_ratios="resources/automatic/prepare/sector_ratios.csv",
    log:
        "logs/prepare/prepare_sector_ratios.log",
    conda:
        "../envs/prepare.yaml"
    script:
        "../scripts/prepare_sector_ratios.py"


rule prepare_sector_ratios_intermediate:
    params:
        industry=config["industry"],
    input:
        industry_sector_ratios=rules.prepare_sector_ratios.output.industry_sector_ratios,
        industrial_energy_demand_per_country_today=rules.prepare_current_energy_demand_per_country.output.current_energy_demand,
        industrial_production_per_country=rules.prepare_future_aggregated_production.output.future,
    output:
        industry_sector_ratios="resources/automatic/prepare/sector_ratios_intermediate_{year}.csv",
    log:
         "logs/prepare/prepare_sector_ratios_intermediate_{year}.log"
    conda:
        "../envs/prepare.yaml"
    script:
        "../scripts/prepare_sector_ratios_intermediate.py"
