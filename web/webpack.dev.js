const { merge } = require('webpack-merge');
const base = require('./webpack.base.js')

module.exports = merge(base, {
    mode: 'development',
    devtool: 'eval',
    devServer: {
        historyApiFallback: true,
        port: 8080,
    },
})