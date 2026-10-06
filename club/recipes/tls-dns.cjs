// Disposable local TLS/DNS relay. Test certificate only, no published port.
const fs=require('fs'),https=require('https'),dgram=require('dgram'),os=require('os');
https.createServer({key:fs.readFileSync('/state/tls/key.pem'),cert:fs.readFileSync('/state/tls/cert.pem')},(req,res)=>{
 const r=https.request({host:'192.168.1.25',port:443,servername:'agence.digiconseil.fr',path:req.url,method:req.method,headers:{...req.headers,host:req.headers.host,cookie:''}},r=>{res.writeHead(r.statusCode,r.headers);r.pipe(res)});r.on('error',()=>{res.writeHead(502);res.end('fixture relay failed')});req.pipe(r)
}).listen(443);
const dns=dgram.createSocket('udp4');dns.on('message',(msg,client)=>{let pos=12,labels=[];while(msg[pos]){let n=msg[pos++];labels.push(msg.subarray(pos,pos+n).toString());pos+=n}pos++;let name=labels.join('.'),type=msg.readUInt16BE(pos),end=pos+4;
 if(name==='artefacts.digiconseil.fr'||name.endsWith('.artefacts.digiconseil.fr')){
  let q=Buffer.from(msg.subarray(0,end));q.writeUInt16BE(0x8180,2);q.writeUInt16BE(type===1?1:0,6);q.writeUInt16BE(0,8);q.writeUInt16BE(0,10);
  if(type===1){let a=Buffer.alloc(16);a.writeUInt16BE(0xc00c,0);a.writeUInt16BE(1,2);a.writeUInt16BE(1,4);a.writeUInt32BE(10,6);a.writeUInt16BE(4,10);os.networkInterfaces().eth0.find(x=>x.family==='IPv4').address.split('.').forEach((v,i)=>a[12+i]=+v);q=Buffer.concat([q,a])}dns.send(q,client.port,client.address)
 }else{const f=dgram.createSocket('udp4');f.on('message',r=>{dns.send(r,client.port,client.address);f.close()});f.send(msg,53,'192.168.1.1');setTimeout(()=>{try{f.close()}catch{}},3000)}});dns.bind(53);console.log('Local fixture ready');
