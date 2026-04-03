FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

RUN npm run build

# Copy application files
COPY . .

EXPOSE 5006

CMD ["npm", "start"]
