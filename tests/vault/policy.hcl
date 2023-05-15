path "auth/token/lookup" {
  capabilities = ["read"]
}
path "auth/token/renew" {
  capabilities = ["update"]
}
path "auth/token/revoke" {
  capabilities = ["update"]
}
path "testapp-1/config" {
  capabilities = ["read", "list", "update"]
}
path "testapp-1/metadata/configuration/*" {
  capabilities = ["read", "list"]
}
path "testapp-1/data/configuration/*" {
  capabilities = ["create", "read", "update", "list"]
}