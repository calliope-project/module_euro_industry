
rule prepare_ammonia_production:
    input:
        usgs=rules.download_ammonia_usgs.output.file,
    output:
        prepared="resources/automatic/prepared/ammonia_production.csv",
    log:
        "logs/prepare/prepare_ammonia_production.log"
    conda:
        "../envs/prepare.yaml"
    script:
        "../scripts/prepare_ammonia_production.py"


rule prepare_current_aggregated_production:
    params:
        industry=config["industry"],
        countries=config["countries"],
    input:
        ch_industrial_production=rules.download_CHE_industry.output.file,
        ammonia_production=rules.prepare_ammonia_production.output.prepared,
        jrc_dir="resources/automatic/jrc_idees/",
        eurostat_dir="resources/automatic/eurostat/",
    output:
        production_per_country="results/aggregated/current_production.csv",
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


rule prepare_sector_ratios:
    params:
        industry=config["industry"],
        ammonia=config["ammonia"],
    input:
        ammonia_production=rules.prepare_ammonia_production.output.prepared,
        idees="resources/automatic/jrc_idees",
    output:
        industry_sector_ratios="resources/automatic/prepared/sector_ratios.csv",
    log:
        "logs/prepare/prepare_sector_ratios.log",
    conda:
        "../envs/prepare.yaml"
    script:
        "../scripts/prepare_sector_ratios.py"
