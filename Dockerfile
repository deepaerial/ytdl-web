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
CMD ["npm", "start"]
########### production ###################
FROM nginx:stable-alpine as prod
COPY --from=stage /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]