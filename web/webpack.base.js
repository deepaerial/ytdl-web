const path = require('path');
const webpack = require("webpack");
const HtmlWebpackPlugin = require('html-webpack-plugin');


module.exports = {
    entry: path.resolve(__dirname, './src/index.js'),
    output: {
        path: path.resolve(__dirname, './dist/'),
        filename: 'app.js',
    },
    module: {
        rules: [
            {
                test: /\.(js|jsx)$/,
                exclude: /node_modules/,
                use: [{ loader: "babel-loader" }]
            },
            {
                test: /\.css$/i,
                use: [{ loader: 'style-loader' }, { loader: 'css-loader' }],
            },
        ]
    },
    plugins: [
        new HtmlWebpackPlugin({
            template: './public/index.html',
            filename: 'index.html',
            favicon: './public/favicon.ico'
        }),
        new webpack.DefinePlugin({
            API_URL: JSON.stringify(process.env.API_URL)
        })
    ],
    resolve: {
        alias: {
            '@mui/styled-engine': '@mui/styled-engine-sc'
        },
    },
};