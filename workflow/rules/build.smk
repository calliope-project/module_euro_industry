
rule build_current_industrial_energy_demand_per_country:
    params:
        countries=config["countries"],
        industry=config["industry"],
        ammonia=config["ammonia"],
    input:
        transformation_output_coke=rules.prepare_coke_transformation.output.coke,
        jrc="resources/automatic/jrc_idees",
        industrial_production_per_country=rules.prepare_current_aggregated_production.output.production_per_country,
    output:
        current_energy_demand="resources/automatic/build/current_industrial_energy_demand_per_country.csv"
    log:
        "logs/build/build_current_industrial_energy_demand_per_country.log"
    conda:
        "../envs/prepare.yaml"
    script:
        "../scripts/build_current_industrial_energy_demand_per_country.py"


rule build_current_disaggregated_industrial_energy_demand:
    input:
        industrial_distribution_key=rules.disaggregate_production_key.output.industrial_distribution_key,
        industrial_energy_demand_per_country_today=rules.build_current_industrial_energy_demand_per_country.output.current_energy_demand,
    output:
        industrial_energy_demand_per_node_today="resources/automatic/build/current_disaggregated_industrial_energy_demand.csv",
    log:
         "logs/build/build_current_disaggregated_industrial_energy_demand.log",
    conda:
        "../envs/prepare.yaml"
    script:
        "../scripts/build_current_disaggregated_industrial_energy_demand.py"
