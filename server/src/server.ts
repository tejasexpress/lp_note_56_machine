import express from 'express';
import dotenv from 'dotenv';
import createPosition from './routes/createPosition';
import sellPosition from './routes/sellPosition';
import getPos from './routes/getPos';
import getPairs from './routes/getInvestablePools';
import cors from 'cors';
import addLiquidity from './routes/addLiquidity';
import update from './routes/updatePositions';
dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;


const requestLogger = (req: express.Request, res: express.Response, next: express.NextFunction) => {
    const start = Date.now();
    
    res.on('finish', () => {
        const duration = Date.now() - start;
        console.log(`${req.method} ${req.originalUrl} - ${res.statusCode} [${duration}ms]`);
    });

    next();
};

app.use(cors())

app.use(express.json());
app.use(requestLogger);

app.use('/buy', createPosition);
app.use('/sell', sellPosition);
app.use('/', getPos)
app.use('/', getPairs);
app.use('/', addLiquidity);
app.use('/', update);

app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
