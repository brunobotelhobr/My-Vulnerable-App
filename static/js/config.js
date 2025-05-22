// Função para pegar o token do cookie
function getAuthToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'token') {
            return value;
        }
    }
    return null;
}

// Função para fazer backup do carrinho
async function backupCart() {
    try {
        // Pega o token de autenticação do cookie
        const token = getAuthToken();
        if (!token) {
            alert('Authentication token not found');
            return;
        }

        // Faz a requisição para exportar o carrinho
        const response = await fetch('/api/cart/export', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || `HTTP error! status: ${response.status}`);
        }

        // Pega os dados do carrinho
        const data = await response.json();
        
        // Cria um blob com os dados base64 do carrinho
        const blob = new Blob([data.cart_data], { type: 'text/plain' });
        
        // Cria um link para download
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'cart_backup.dat';
        
        // Adiciona o link ao documento e clica nele
        document.body.appendChild(a);
        a.click();
        
        // Limpa o link
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    } catch (error) {
        console.error('Error backing up cart:', error);
        alert(error.message || 'Unknown error occurred while backing up cart');
    }
}

// Função para restaurar o carrinho
async function restoreCart(event) {
    try {
        // Pega o token de autenticação do cookie
        const token = getAuthToken();
        if (!token) {
            alert('Authentication token not found');
            return;
        }

        // Pega o arquivo selecionado
        const file = event.target.files[0];
        if (!file) {
            return;
        }

        // Lê o arquivo como texto
        const reader = new FileReader();
        reader.onload = async (e) => {
            try {
                // Pega o conteúdo base64 do arquivo
                const cart_data = e.target.result;

                // Envia os dados para a API como query parameter
                const response = await fetch(`/api/cart/import?cart_data=${encodeURIComponent(cart_data)}`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.detail || `Failed to restore cart (HTTP ${response.status})`);
                }

                // Recarrega a página para mostrar o carrinho atualizado
                window.location.reload();
            } catch (error) {
                console.error('Error restoring cart:', error);
                alert(error.message || 'Unknown error occurred while restoring cart');
            }
        };

        reader.readAsText(file);
    } catch (error) {
        console.error('Error reading file:', error);
        alert(error.message || 'Unknown error occurred while reading file');
    }
} 