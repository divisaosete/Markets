export class Poller {
  constructor(task,{document:doc=globalThis.document,interval=60000,setInterval:every=globalThis.setInterval,clearInterval:clear=globalThis.clearInterval}={}){
    this.doc=doc;this.task=task;this.running=false;this.pending=false;this.stopped=false;this.clear=clear;
    this.resume=()=>{if(!doc.hidden)this.refresh()};doc.addEventListener('visibilitychange',this.resume);
    this.timer=every(()=>{if(!doc.hidden)this.refresh()},interval);
  }
  async refresh(){
    if(this.stopped||this.doc.hidden)return;
    if(this.running){this.pending=true;return}
    this.running=true;
    try{await this.task()}finally{this.running=false;if(this.pending){this.pending=false;if(!this.stopped&&!this.doc.hidden)return this.refresh()}}
  }
  stop(){this.stopped=true;this.clear(this.timer);this.doc.removeEventListener('visibilitychange',this.resume)}
}
