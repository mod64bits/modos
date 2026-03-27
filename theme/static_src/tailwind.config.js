/**
 * Ficheiro de configuração do Tailwind CSS.
 * Este ficheiro é o "mapa" que diz ao compilador onde estão os seus HTMLs.
 * Se os caminhos estiverem errados, o Tailwind apaga as classes em produção (Purge).
 */
module.exports = {
    content: [
        // Procura na pasta templates padrão do tema
        '../templates/**/*.html',
        // Procura na pasta templates da raiz do projeto
        '../../templates/**/*.html',
        // MÁGICA AQUI: Diz ao Tailwind para ler ABSOLUTAMENTE TODOS
        // os ficheiros HTML dentro da sua pasta 'apps'
        '../../apps/**/*.html',
        '../../apps/**/templates/**/*.html',
    ],
    theme: {
        extend: {},
    },
    plugins: [
        /**
         * Plugins oficiais que garantem que formulários e tipografia
         * ficam com aspeto profissional por defeito.
         */
        require('@tailwindcss/forms'),
        require('@tailwindcss/typography'),
        require('@tailwindcss/aspect-ratio'),
    ],
}