# For the correct receipt of the token via approle
path "auth/token/lookup" {
  capabilities = ["read"]
}
# To revoke the token after creating and testing approle
path "auth/token/revoke" {
  capabilities = ["update"]
}
# To lookup for a token that has expired
path "auth/token/lookup-self" {
  capabilities = ["read"]
}
# To read and update the namespace configuration
path "testapp-1/config" {
  capabilities = ["read", "list", "update"]
}
# To get a list of secrets
path "testapp-1/metadata/configuration/*" {
  capabilities = ["read", "list"]
}
# To work with secret apllication data
path "testapp-1/data/configuration/*" {
  capabilities = ["create", "read", "update", "list"]
}