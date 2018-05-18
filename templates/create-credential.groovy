#!groovy
import jenkins.model.*
import com.cloudbees.plugins.credentials.*
import com.cloudbees.plugins.credentials.common.*
import com.cloudbees.plugins.credentials.domains.*
import com.cloudbees.plugins.credentials.*
import com.cloudbees.plugins.credentials.impl.*
import hudson.util.Secret
import org.jenkinsci.plugins.plaincredentials.impl.StringCredentialsImpl

domain = Domain.global()
store = SystemCredentialsProvider.getInstance().getStore()

credentialType = "{{ credential.type | default('username-password') }}"
credential = getCredential(credentialType)

def success = store.addCredentials(domain, credential)
if (success) {
  println "Created credential with id {{ credential.id }}"
} else {
  // Need to update the credential which requires the old one
  for (cred in store.getCredentials(domain)) {
    if (cred.getId().equals("{{ credential.id }}")) {
      store.updateCredentials(domain, cred, credential)
      println "Updated credential with id {{ credential.id }}"
      break
    }
  }
}

private BaseStandardCredentials getCredential(credentialType) {
  if (credentialType == "username-password") {
    return new UsernamePasswordCredentialsImpl(
      CredentialsScope.GLOBAL,
      "{{ credential.id }}",
      "{{ credential.description | default('') }}",
      "{{ credential.username | default('') }}",
      "{{ credential.password | default('') }}"
    )
  } else if (credentialType == "string") {
    return new StringCredentialsImpl(
      CredentialsScope.GLOBAL,
      "{{ credential.id }}",
      "{{ credential.description | default('') }}",
      new Secret("{{ credential.secret | default('') }}")
    )
  } else if (credentialType == "VaultTokenFileCredential") {
    return new com.datapipe.jenkins.vault.credentials.VaultTokenFileCredential(
      CredentialsScope.GLOBAL,
      "{{ credential.id }}",
      "{{ credential.description | default('') }}",
      "{{ credential.filepath | default('') }}"
    )
  } else if (credentialType == "azure") {
    return new com.microsoft.azure.util.AzureCredentials(
      CredentialsScope.GLOBAL,
      "{{ credential.id }}",
      "{{ credential.description | default('') }}",
      "{{ credential.subscriptionId | default('') }}",
      "{{ credential.clientId | default('') }}",
      "{{ credential.clientSecret | default('') }}",
      "{{ credential.oauth2TokenEndpoint | default('') }}",
      "{{ credential.serviceManagementURL | default('https://management.core.windows.net/') }}",
      "{{ credential.authenticationEndpoint | default('https://login.microsoftonline.com/') }}",
      "{{ credential.resourceManagerEndpoint | default('https://management.azure.com/') }}",
      "{{ credential.graphEndpoint | default('https://graph.windows.net/') }}"
    )
  } else if (credentialType == "ssh") {
    return new com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey(
      CredentialsScope.GLOBAL,
      "{{ credential.id }}",
      "{{ credential.username | default('jenkins') }}",
        new com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey.FileOnMasterPrivateKeySource("{{ credential.private_key_location | default('') }}"),
        null,
      "{{ credential.description | default('') }}")
  } else {
    throw new IllegalArgumentException("Unknown credential type: ${credentialType}")
  }
}
