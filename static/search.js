(function(){
    const cryptoAssets = [
        { label: 'Bitcoin', href: '/tracker?type=crypto&asset=bitcoin', symbol: 'BTC', type: 'crypto' },
        { label: 'Ethereum', href: '/tracker?type=crypto&asset=ethereum', symbol: 'ETH', type: 'crypto' }
    ];
    const stockAssets = [
        { label: 'Apple', href: '/tracker?type=stocks&asset=AAPL', symbol: 'AAPL', type: 'stocks' },
        { label: 'NVIDIA', href: '/tracker?type=stocks&asset=NVDA', symbol: 'NVDA', type: 'stocks' }
    ];
    const allAssets = [...cryptoAssets, ...stockAssets];

    const searchInput = document.getElementById('searchInput');
    const searchResults = document.getElementById('searchResults');

    function renderResults(query) {
        searchResults.innerHTML = '';
        if (!query.trim()) return;
        
        const matches = allAssets.filter(asset => 
            asset.label.toLowerCase().includes(query.toLowerCase()) ||
            asset.symbol.toLowerCase().includes(query.toLowerCase())
        ).slice(0, 8);

        matches.forEach(asset => {
            const li = document.createElement('li');
            li.className = 'search-result-item';
            li.innerHTML = `<strong>${asset.label}</strong> <span class="asset-type">${asset.symbol} • ${asset.type.toUpperCase()}</span>`;
            li.tabIndex = 0;
            li.addEventListener('click', () => {
                window.location.href = asset.href;
            });
            li.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') window.location.href = asset.href;
            });
            searchResults.appendChild(li);
        });
    }

    searchInput.addEventListener('input', (e) => {
        renderResults(e.target.value);
    });

    searchInput.addEventListener('focus', (e) => {
        renderResults(e.target.value);
    });

    document.addEventListener('click', (e) => {
        if (!e.composedPath().includes(document.querySelector('.search-bar-container'))) {
            searchResults.innerHTML = '';
        }
    });
})();