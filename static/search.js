(function(){
    const cryptoAssets = [
        { label: 'Bitcoin', href: '/tracker?type=crypto&asset=bitcoin', symbol: 'BTC', type: 'crypto' },
        { label: 'Ethereum', href: '/tracker?type=crypto&asset=ethereum', symbol: 'ETH', type: 'crypto' },
        { label: 'Cardano', href: '/tracker?type=crypto&asset=cardano', symbol: 'ADA', type: 'crypto' },
        { label: 'Solana', href: '/tracker?type=crypto&asset=solana', symbol: 'SOL', type: 'crypto' },
        { label: 'Ripple', href: '/tracker?type=crypto&asset=ripple', symbol: 'XRP', type: 'crypto' },
        { label: 'Polkadot', href: '/tracker?type=crypto&asset=polkadot', symbol: 'DOT', type: 'crypto' },
        { label: 'Dogecoin', href: '/tracker?type=crypto&asset=dogecoin', symbol: 'DOGE', type: 'crypto' },
        { label: 'Litecoin', href: '/tracker?type=crypto&asset=litecoin', symbol: 'LTC', type: 'crypto' },
        { label: 'Chainlink', href: '/tracker?type=crypto&asset=chainlink', symbol: 'LINK', type: 'crypto' },
        { label: 'Bitcoin Cash', href: '/tracker?type=crypto&asset=bitcoincash', symbol: 'BCH', type: 'crypto' },
        { label: 'Binance Coin', href: '/tracker?type=crypto&asset=binance', symbol: 'BNB', type: 'crypto' },
        { label: 'Avalanche', href: '/tracker?type=crypto&asset=avalanche', symbol: 'AVAX', type: 'crypto' },
        { label: 'Polygon', href: '/tracker?type=crypto&asset=polygon', symbol: 'MATIC', type: 'crypto' }
    ];
    const stockAssets = [
        { label: 'Apple', href: '/tracker?type=stocks&asset=AAPL', symbol: 'AAPL', type: 'stocks' },
        { label: 'Google', href: '/tracker?type=stocks&asset=GOOGL', symbol: 'GOOGL', type: 'stocks' },
        { label: 'Microsoft', href: '/tracker?type=stocks&asset=MSFT', symbol: 'MSFT', type: 'stocks' },
        { label: 'Tesla', href: '/tracker?type=stocks&asset=TSLA', symbol: 'TSLA', type: 'stocks' },
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