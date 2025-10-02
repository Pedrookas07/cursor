/**
 * Cloudflare Worker para receber logs do Slack
 * 
 * Este Worker recebe logs enviados pelo pipeline Python
 * e os armazena para análise posterior.
 */

export default {
    async fetch(request, env, ctx) {
        const url = new URL(request.url);

        // CORS headers para permitir requisições
        const corsHeaders = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        };

        // Handle CORS preflight
        if (request.method === 'OPTIONS') {
            return new Response(null, { status: 204, headers: corsHeaders });
        }

        try {
            // Rota principal - endpoint para receber logs
            if (url.pathname === '/ingest' && request.method === 'POST') {
                return await handleLogIngest(request, env, corsHeaders);
            }

            // Rota para listar logs armazenados
            if (url.pathname === '/logs' && request.method === 'GET') {
                return await handleGetLogs(request, env, corsHeaders);
            }

            // Rota para estatísticas
            if (url.pathname === '/stats' && request.method === 'GET') {
                return await handleGetStats(request, env, corsHeaders);
            }

            // Rota raiz - página de status
            if (url.pathname === '/') {
                return new Response(`
          <!DOCTYPE html>
          <html>
          <head>
            <title>Rebuss Log Bot - Worker Status</title>
            <meta charset="utf-8">
            <style>
              body { font-family: Arial, sans-serif; margin: 40px; }
              .status { color: #28a745; font-weight: bold; }
              .endpoint { background: #f8f9fa; padding: 10px; margin: 10px 0; border-radius: 5px; }
            </style>
          </head>
          <body>
            <h1>🤖 Rebuss Log Bot Worker</h1>
            <p class="status">✅ Worker Online</p>
            <p>Endpoints disponíveis:</p>
            <div class="endpoint">
              <strong>POST /ingest</strong> - Receber logs do Slack
            </div>
            <div class="endpoint">
              <strong>GET /logs</strong> - Listar logs armazenados
            </div>
            <div class="endpoint">
              <strong>GET /stats</strong> - Estatísticas dos logs
            </div>
            <p><small>Timestamp: ${new Date().toISOString()}</small></p>
          </body>
          </html>
        `, {
                    headers: { ...corsHeaders, 'Content-Type': 'text/html; charset=utf-8' }
                });
            }

            return new Response('Not Found', {
                status: 404,
                headers: corsHeaders
            });

        } catch (error) {
            console.error('Worker error:', error);
            return new Response(JSON.stringify({
                error: 'Internal Server Error',
                message: error.message
            }), {
                status: 500,
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });
        }
    }
};

/**
 * Processa logs recebidos do pipeline Python
 */
async function handleLogIngest(request, env, corsHeaders) {
    try {
        const data = await request.json();

        // Validar estrutura dos dados
        if (!data.logs || !Array.isArray(data.logs)) {
            return new Response(JSON.stringify({
                error: 'Invalid payload',
                message: 'Expected logs array'
            }), {
                status: 400,
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });
        }

        console.log(`Recebidos ${data.logs.length} logs do Rebuss`);

        // Processar cada log
        const processedLogs = [];
        const errorStats = {
            by_app: {},
            by_error_code: {},
            by_inventory: {},
            by_user: {}
        };

        for (const log of data.logs) {
            const processedLog = {
                id: generateLogId(),
                timestamp: log.timestamp || new Date().toISOString(),
                channel: log.channel,
                user: log.user,
                text: log.text,
                log_level: log.log_level,
                machine_info: log.machine_info,
                user_info: log.user_info,
                error_details: log.error_details,
                source: log.source || 'rebuss_machine_log',
                received_at: new Date().toISOString(),
                metadata: data.metadata || {}
            };

            processedLogs.push(processedLog);

            // Estatísticas para análise
            const appType = extractAppType(processedLog.text);
            const errorCode = processedLog.error_details?.code || 'UNKNOWN';
            const inventoryId = processedLog.machine_info?.inventory_id || 'UNKNOWN';
            const userName = processedLog.user_info?.user_name || 'UNKNOWN';

            errorStats.by_app[appType] = (errorStats.by_app[appType] || 0) + 1;
            errorStats.by_error_code[errorCode] = (errorStats.by_error_code[errorCode] || 0) + 1;
            errorStats.by_inventory[inventoryId] = (errorStats.by_inventory[inventoryId] || 0) + 1;
            errorStats.by_user[userName] = (errorStats.by_user[userName] || 0) + 1;

            // Log para console (aparece nos logs do Worker)
            console.log(`[${processedLog.log_level || 'UNKNOWN'}] ${appType} ${errorCode} - ${inventoryId} - ${processedLog.text.substring(0, 80)}...`);
        }

        // Armazenar logs (aqui você pode usar KV, D1, ou outro storage)
        if (env.LOGS_KV) {
            for (const log of processedLogs) {
                await env.LOGS_KV.put(`log:${log.id}`, JSON.stringify(log));
            }
        }

        // Resposta de sucesso com estatísticas
        return new Response(JSON.stringify({
            success: true,
            message: `Processados ${processedLogs.length} logs do sistema Rebuss`,
            processed_count: processedLogs.length,
            statistics: errorStats,
            timestamp: new Date().toISOString()
        }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });

    } catch (error) {
        console.error('Erro ao processar logs:', error);
        return new Response(JSON.stringify({
            error: 'Failed to process logs',
            message: error.message
        }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
}

/**
 * Retorna logs armazenados
 */
async function handleGetLogs(request, env, corsHeaders) {
    try {
        const url = new URL(request.url);
        const limit = parseInt(url.searchParams.get('limit') || '50');
        const level = url.searchParams.get('level');

        let logs = [];

        if (env.LOGS_KV) {
            // Listar todas as chaves de logs
            const keys = await env.LOGS_KV.list({ limit: limit * 2 });

            for (const key of keys.keys) {
                if (key.name.startsWith('log:')) {
                    const logData = await env.LOGS_KV.get(key.name);
                    if (logData) {
                        const log = JSON.parse(logData);

                        // Filtrar por nível se especificado
                        if (!level || log.log_level === level) {
                            logs.push(log);
                        }
                    }
                }
            }
        }

        // Ordenar por timestamp (mais recente primeiro)
        logs.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
        logs = logs.slice(0, limit);

        return new Response(JSON.stringify({
            logs: logs,
            count: logs.length,
            timestamp: new Date().toISOString()
        }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });

    } catch (error) {
        return new Response(JSON.stringify({
            error: 'Failed to retrieve logs',
            message: error.message
        }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
}

/**
 * Retorna estatísticas dos logs
 */
async function handleGetStats(request, env, corsHeaders) {
    try {
        let stats = {
            total_logs: 0,
            by_level: {},
            by_machine: {},
            recent_activity: null,
            timestamp: new Date().toISOString()
        };

        if (env.LOGS_KV) {
            const keys = await env.LOGS_KV.list({ limit: 1000 });

            for (const key of keys.keys) {
                if (key.name.startsWith('log:')) {
                    const logData = await env.LOGS_KV.get(key.name);
                    if (logData) {
                        const log = JSON.parse(logData);

                        stats.total_logs++;

                        // Contar por nível
                        const level = log.log_level || 'UNKNOWN';
                        stats.by_level[level] = (stats.by_level[level] || 0) + 1;

                        // Contar por máquina
                        if (log.machine_info?.hostname) {
                            const machine = log.machine_info.hostname;
                            stats.by_machine[machine] = (stats.by_machine[machine] || 0) + 1;
                        }

                        // Última atividade
                        if (!stats.recent_activity || new Date(log.timestamp) > new Date(stats.recent_activity)) {
                            stats.recent_activity = log.timestamp;
                        }
                    }
                }
            }
        }

        return new Response(JSON.stringify(stats), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });

    } catch (error) {
        return new Response(JSON.stringify({
            error: 'Failed to get stats',
            message: error.message
        }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
}

/**
 * Extrai tipo de app do texto do log
 */
function extractAppType(text) {
    if (!text) return 'UNKNOWN';
    const match = text.match(/^(\w+)\s+error/);
    return match ? match[1] : 'UNKNOWN';
}

/**
 * Gera ID único para log
 */
function generateLogId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
}
