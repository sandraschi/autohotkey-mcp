# Per-repo fleet start config for autohotkey-mcp
# Edit ports/backend target here - start.ps1 is fleet-standard.
@{
    Name         = 'autohotkey-mcp'
    BackendPort  = 10746
    FrontendPort = 10747
    HealthPath   = '/health'
    WebRoot      = 'D:\Dev\repos\autohotkey-mcp\web_sota'
    Backend = @{
        Kind          = 'uvicorn'
        UvicornTarget = 'autohotkey_mcp.server:app'
        SyncExtras    = @('dev')
        Env           = @{ WEB_PORT = '10746' }
    }
    Frontend = @{
        Kind           = 'vite-npm'
        PackageManager = 'npm'
        PortEnvVar     = 'VITE_PORT'
        ApiTargetEnv   = 'VITE_API_TARGET'
    }
}
