

rule disaggregate_production_rates:
    message:
        "{wildcards.shape}: disaggregating production using proxies."
    params:
        hotmaps_locate_missing=config["industry"]["hotmaps_locate_missing"],
        geographic_crs=internal["crs"]["geographic"]
    input:
        shapes=rules.prepare_shapes.output.shapes,
        hotmaps=rules.download_hotmaps.output.file,
        gem_gspt=rules.download_GEM_SPT.output.file,
        ammonia=rules.download_ammonia_plants.output.file,
        cement_supplement=rules.download_cement_non_eu.output.file,
        refineries_supplement=rules.download_refineries_non_eu.output.file,
    output:
        production_rates="resources/automatic/shapes/{shape}/production_rates.csv",
    log:
        "logs/{shape}/disaggregate_production_rates.log",
    conda:
        "../envs/prepare.yaml"
    script:
        "../scripts/disaggregate_production_rates.py"


rule disaggregate_current_energy_demand:
    input:
        shapes=rules.prepare_shapes.output.shapes,
        shape_ratios=rules.disaggregate_production_rates.output.production_rates,
        current_national_energy_demand=rules.prepare_current_europe_energy_demand.output.energy_demand,
    output:
        demand_per_shape="results/{shape}/current_industrial_energy_demand.csv",
    log:
        "logs/disaggregated/disaggregate_current_energy_demand_{shape}.log",
    conda:
        "../envs/prepare.yaml"
    script:
        "../scripts/disaggregate_current_energy_demand.py"


rule disaggregate_future_production:
    input:
        shapes=rules.prepare_shapes.output.shapes,
        ratios=rules.disaggregate_production_rates.output.production_rates,
        future_national_production=rules.prepare_future_europe_production.output.production,
    output:
        production="results/{shape}/{year}/future_production.csv",
    log:
        "logs/disaggregate/disaggregate_future_production_{shape}_{year}.log",
    conda:
        "../envs/prepare.yaml"
    script:
        "../scripts/disaggregate_future_production.py"


rule disaggregate_future_energy_demand:
    input:
        shapes=rules.prepare_shapes.output.shapes,
        sector_ratios=rules.prepare_future_europe_sector_rates.output.sector_rates,
        disaggregated_future_production=rules.disaggregate_future_production.output.production,
        disaggregated_current_energy_demand=rules.disaggregate_current_energy_demand.output.demand_per_shape,
    output:
        energy_demand="results/{shape}/{year}/future_energy_demand.csv",
    log:
        "logs/disaggregate/disaggregate_future_industrial_energy_demand_{shape}_{year}.log",
    conda:
        "../envs/prepare.yaml"
    script:
        "../scripts/disaggregate_future_energy_demand.py"
