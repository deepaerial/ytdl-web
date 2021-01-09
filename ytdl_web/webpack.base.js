const path = require('path');
const dotenv = require('dotenv');
const webpack = require("webpack");
const HtmlWebpackPlugin = require('html-webpack-plugin');


dotenv_parsed = dotenv.config().parsed

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
                use: {
                    loader: 'babel-loader',
                }
            }
        ]
    },
    plugins: [
        new HtmlWebpackPlugin({
            template: './src/index.html',
            filename: 'index.html'
        }),
        new webpack.DefinePlugin({
            API_URL: JSON.stringify(dotenv_parsed.API_URL)
        }),

    ]
};