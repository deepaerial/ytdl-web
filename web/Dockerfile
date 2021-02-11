FROM node:12-alpine3.10 as base
WORKDIR /app
ENV PATH /app/node_modules/.bin:$PATH
COPY package.json ./
COPY package-lock.json ./
RUN npm install
COPY . .
########### development ##################
FROM base as dev
WORKDIR /app
EXPOSE 8080
CMD ["webpack-dev-server", "--config", "webpack.dev.js", "--host", "0.0.0.0"]
########### production ###################
FROM dev as prod
RUN npm run build
COPY /app/build /usr/share/nginx/html
CMD ["nginx", "-g", "daemon off;"]