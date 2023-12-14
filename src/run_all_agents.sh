#!/bin/bash

# Define your agents here
declare -a agents=("DisconnectingAgent" "IllegalMessageAgent" "NaiveAgent" "NoConnectionAgent" "SelfTerminatingAgent" "TimeoutAgent" "TooLongMessageAgent")

# File to store results
result_file="agent_results.txt"

# Clear the result file at the start
> $result_file

# Function to run an agent
run_agent() {
    agent=$1
    echo "Running agent: $agent"
    # The command to run your agent, modify as needed
    output=$(python3 Hex.py "a=our_agent;python3 src/Communicator.py" "a=$agent;python3 agents/DefaultAgents/$agent.py" -v)
    echo "Outcome for $agent: $output"
    echo "$agent: $output" >> $result_file
}

# Iterate over the agents and run them
for agent in "${agents[@]}"; do
    run_agent "$agent"
done

echo "All agents have been run. Results saved in $result_file."
