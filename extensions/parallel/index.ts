/**
 * Parallel.ai Plugin
 * Adds parallel_web_search and parallel_extract tools
 */

export default function register(api: any) {
  
  // ============================================
  // parallel_web_search - Search the web
  // ============================================
  api.registerTool({
    name: 'parallel_web_search',
    description: 'Search the web using Parallel.ai. Returns ranked URLs with extended excerpts. Better than web_search for research tasks.',
    
    parameters: {
      type: 'object',
      properties: {
        query: {
          type: 'string',
          description: 'Natural language search query or objective',
        },
        count: {
          type: 'number',
          description: 'Number of results to return (1-10)',
          default: 5,
        },
      },
      required: ['query'],
    },
    
    async execute(_id: string, params: { query: string; count?: number }) {
      const { query, count = 5 } = params;
      const apiKey = getApiKey();
      
      if (!apiKey) {
        return errorResponse('PARALLEL_API_KEY environment variable not set');
      }
      
      try {
        const response = await fetch('https://api.parallel.ai/v1beta/search', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'x-api-key': apiKey,
            'parallel-beta': 'search-extract-2025-10-10',
          },
          body: JSON.stringify({
            objective: query,
            max_results: Math.min(count, 10),
            excerpts: {
              max_chars_per_result: 2000,
            },
          }),
        });
        
        if (!response.ok) {
          const errorText = await response.text();
          return errorResponse(`Parallel.ai API error (${response.status}): ${errorText}`);
        }
        
        const data = await response.json();
        
        const results = data.results?.map((r: any) => ({
          title: r.title || '',
          url: r.url || '',
          snippet: r.excerpts?.join(' ... ') || '',
          description: r.excerpts?.join(' ... ') || '',
          publishedDate: r.publish_date || undefined,
        })) || [];
        
        return jsonResponse({
          query,
          provider: 'parallel',
          count: results.length,
          results,
        });
        
      } catch (error: any) {
        return errorResponse(`Parallel search failed: ${error.message || 'Unknown error'}`);
      }
    },
  });

  // ============================================
  // parallel_extract - Extract content from URL
  // ============================================
  api.registerTool({
    name: 'parallel_extract',
    description: 'Extract clean markdown content from a URL using Parallel.ai. Handles JavaScript-heavy pages and PDFs. Can focus excerpts on a specific objective.',
    
    parameters: {
      type: 'object',
      properties: {
        url: {
          type: 'string',
          description: 'The URL to extract content from',
        },
        objective: {
          type: 'string',
          description: 'Optional: Focus excerpts on this objective (e.g., "pricing information")',
        },
        full_content: {
          type: 'boolean',
          description: 'Return full page content instead of focused excerpts',
          default: false,
        },
      },
      required: ['url'],
    },
    
    async execute(_id: string, params: { url: string; objective?: string; full_content?: boolean }) {
      const { url, objective, full_content = false } = params;
      const apiKey = getApiKey();
      
      if (!apiKey) {
        return errorResponse('PARALLEL_API_KEY environment variable not set');
      }
      
      try {
        const body: any = {
          urls: [url],
        };
        
        if (objective) {
          body.objective = objective;
        }
        
        if (full_content) {
          body.excerpts = { include_full_content: true };
        } else {
          body.excerpts = { max_chars_per_result: 4000 };
        }
        
        const response = await fetch('https://api.parallel.ai/v1beta/extract', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'x-api-key': apiKey,
          },
          body: JSON.stringify(body),
        });
        
        if (!response.ok) {
          const errorText = await response.text();
          return errorResponse(`Parallel.ai Extract API error (${response.status}): ${errorText}`);
        }
        
        const data = await response.json();
        const result = data.results?.[0];
        
        if (!result) {
          return errorResponse('No content extracted from URL');
        }
        
        return jsonResponse({
          url: result.url,
          title: result.title || '',
          publish_date: result.publish_date || null,
          content: result.excerpts?.join('\n\n---\n\n') || result.full_content || '',
          extract_id: data.extract_id,
        });
        
      } catch (error: any) {
        return errorResponse(`Parallel extract failed: ${error.message || 'Unknown error'}`);
      }
    },
  });
}

// ============================================
// Helpers
// ============================================

function getApiKey(): string | undefined {
  return process.env.PARALLEL_API_KEY;
}

function jsonResponse(data: any) {
  return {
    content: [{
      type: 'text',
      text: JSON.stringify(data, null, 2)
    }]
  };
}

function errorResponse(message: string) {
  return {
    content: [{
      type: 'text',
      text: `Error: ${message}`
    }]
  };
}
