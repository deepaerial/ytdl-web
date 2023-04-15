FROM node:18-alpine as base
ENV PATH /app/node_modules/.bin:$PATH
WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .
########### development ##################
FROM base as dev
COPY --from=base /app/node_modules /app/node_modules
WORKDIR /app
EXPOSE 8080
CMD ["npm", "start"]
########### production ###################
FROM nginx:stable-alpine as prod
COPY --from=stage /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]