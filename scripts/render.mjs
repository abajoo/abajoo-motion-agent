import puppeteer from 'puppeteer';
import {spawn} from 'node:child_process';
import {mkdirSync} from 'node:fs';
import {resolve,dirname} from 'node:path';
import {pathToFileURL} from 'node:url';
const duration=Number(process.env.DURATION??10),fps=30,width=1920,height=1080;
if(!Number.isInteger(duration)||duration<1||duration>300)throw new Error('DURATION must be an integer 1..300');
const input=resolve('projects/erp-gagal/index.html'),output=resolve('output/erp-gagal.mp4');
mkdirSync(dirname(output),{recursive:true});
const browser=await puppeteer.launch({headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});
let encoder;
try{
 const page=await browser.newPage();await page.setViewport({width,height,deviceScaleFactor:1});
 await page.goto(pathToFileURL(input).href+'?capture=1');
 await page.evaluate(d=>window.setDuration(d),duration);
 encoder=spawn('ffmpeg',['-hide_banner','-loglevel','warning','-y','-f','image2pipe','-vcodec','mjpeg','-framerate',String(fps),'-i','pipe:0','-an','-c:v','libx264','-pix_fmt','yuv420p','-preset','veryfast','-crf','24','-movflags','+faststart',output],{stdio:['pipe','inherit','inherit']});
 const completion=new Promise((ok,bad)=>{encoder.once('error',bad);encoder.once('close',code=>code===0?ok():bad(new Error('ffmpeg exit '+code)))});
 for(let i=0;i<duration*fps;i++){
  await page.evaluate(t=>window.renderAt(t),i/fps);
  const frame=await page.screenshot({type:'jpeg',quality:83});
  if(!encoder.stdin.write(frame))await new Promise((ok,bad)=>{encoder.stdin.once('drain',ok);encoder.stdin.once('error',bad)});
  if(i%300===0)console.log('Frame',i,'/',duration*fps);
 }
 encoder.stdin.end();await completion;console.log('MP4 written:',output);
}finally{if(encoder&&encoder.exitCode===null)encoder.kill('SIGTERM');await browser.close();}
