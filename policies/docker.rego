package main

# Deny: Do not use 'latest' tag in FROM images
deny[msg] {
    input[i].Cmd == "from"
    val := input[i].Value
    contains(val[i], ":latest")
    msg := sprintf("Line %d: Do not use 'latest' tag in FROM image: %s", [i, val])
}

# Deny: Do not run as root (USER instruction must be present)
deny[msg] {
    not any_user_instruction
    msg := "Dockerfile must include a USER instruction (do not run as root)"
}

any_user_instruction {
    input[i].Cmd == "user"
}

# Deny: Must include HEALTHCHECK instruction
deny[msg] {
    not any_healthcheck
    msg := "Dockerfile must include a HEALTHCHECK instruction"
}

any_healthcheck {
    input[i].Cmd == "healthcheck"
}

# Warn: Resource limits should be defined (for docker-compose or K8s)
# This is a placeholder for K8s manifests; for Dockerfile we check EXPOSE
warn[msg] {
    not any_expose
    msg := "Dockerfile should expose a port for the application"
}

any_expose {
    input[i].Cmd == "expose"
}