const assert = require('node:assert/strict');
const Module = require('node:module');
const { createHash } = require('node:crypto');
const originalLoad = Module._load;
const providers = new Map();
const commands = [];
const disposable = () => ({dispose(){}});
function uri(path) { return {path,fsPath:path,toString:()=>path}; }
const vscode = {
    Uri: {joinPath:(base,...parts)=>uri([base.path,...parts].join('/'))},
    workspace: {workspaceFolders:[{uri:uri('/workspace')}], fs:{
        readFile:async()=>Buffer.from(JSON.stringify({mode:'server'})), readDirectory:async()=>[],
    }},
    window: {registerWebviewViewProvider:(id,provider)=>{providers.set(id,provider);return disposable();}},
    commands: {executeCommand:async command=>commands.push(command)}, FileType:{File:1},
};
Module._load = function(request,parent,isMain) { return request==='vscode' ? vscode : originalLoad.call(this,request,parent,isMain); };
function view() {
    const messages=[];
    let receive;
    return {visible:true,show(){},onDidDispose:disposable,webview:{
        messages,cspSource:'https://webview.test',asWebviewUri:value=>value,
        onDidReceiveMessage:handler=>{receive=handler;return disposable();},
        postMessage:async message=>{messages.push(structuredClone(message));return true;},
        receive:message=>receive(message),
    }};
}
const account={enabled:true,available:true,defense_required:true,balance_usd:'1',spent_usd:'0',reason:'Доступен'};
function task(id) {return {id,title:'Задача '+id,slug:'basics',version:'1',statement_md:'# '+id+'\n\nReturn 42.',stub_py:'def task_'+id.toLowerCase()+'():\n    pass',hints:[]};}
(async()=>{
    try {
        const {AssistantPanel}=require('../out/assistantPanel.js');
        const {TaskViewPanel}=require('../out/taskViewPanel.js');
        const context={extensionUri:uri('/extension'),subscriptions:[]};
        let code='def task_g1():\n    return 42';
        let created=0,sent=0,checked=[];
        const api={
            getAIAccount:async()=>account,getAISubmissions:async()=>[],getTask:async id=>task(id),
            getHints:async()=>[],
            createAISession:async body=>{
                created++;assert.equal(body.student_code,code);
                return {id:'session-'+body.task_id,task_id:body.task_id,mode:body.mode,status:'active',messages:[],account};
            },
            sendAIMessage:async (id,text,_requestId,freshCode)=>{
                sent++;assert.equal(freshCode,code);
                return {id,task_id:id.replace('session-',''),mode:'hint',status:'active',messages:[{role:'assistant',content:'Разберём цикл.'}],account};
            },
        };
        AssistantPanel.configure(context.extensionUri,()=>api);AssistantPanel.register(context);
        TaskViewPanel.configure(context.extensionUri,{getApi:()=>api,checkTask:async id=>checked.push(id),openPy:async()=>{}});
        TaskViewPanel.register(context);
        assert.deepEqual([...providers.keys()],['egoAssistant','egoTaskDetail']);
        const chat=view(),detail=view();
        providers.get('egoAssistant').resolveWebviewView(chat);
        providers.get('egoTaskDetail').resolveWebviewView(detail);
        await chat.webview.receive({type:'ready'});await detail.webview.receive({type:'ready'});
        await AssistantPanel.show('G1',code,undefined,async()=>code);
        await TaskViewPanel.show({...task('G1'),status:'new'});
        assert.ok(commands.includes('egoAssistant.focus'));
        await chat.webview.receive({type:'assistant.send',taskId:'G1',text:'В чём идея?'});
        assert.equal(created,1);assert.equal(sent,1);
        code='def task_g1():\n    return 43'; // Unsaved code, while the chat owns focus.
        await chat.webview.receive({type:'assistant.send',taskId:'G1',text:'А теперь?'});
        assert.equal(sent,2);
        const g1Session=chat.webview.messages.at(-1).payload.session;
        await AssistantPanel.follow('G3','def task_g3(): pass',async()=> 'def task_g3(): pass');
        await TaskViewPanel.followTask({...task('G3'),status:'new'});
        await chat.webview.receive({type:'assistant.send',taskId:'G1',text:'old queued click'});
        await detail.webview.receive({type:'taskView.check',taskId:'G1'});
        assert.equal(sent,2);assert.deepEqual(checked,[]);
        await detail.webview.receive({type:'taskView.check',taskId:'G3'});
        assert.deepEqual(checked,['G3']);
        await AssistantPanel.follow('G1',code,async()=>code);
        assert.deepEqual(chat.webview.messages.at(-1).payload.session,g1Session);
        // Slow G1 metadata must not overwrite G3 after a rapid switch.
        let resolveG1;
        api.getTask=id=>id==='G1'?new Promise(resolve=>{resolveG1=resolve;}):Promise.resolve(task(id));
        const stale=TaskViewPanel.followTask({...task('G1'),status:'new'});
        await new Promise(resolve=>setImmediate(resolve));
        await TaskViewPanel.followTask({...task('G3'),status:'new'});
        resolveG1(task('G1'));await stale;
        assert.equal(detail.webview.messages.at(-1).payload.id,'G3');
        AssistantPanel.close();
        assert.equal(chat.webview.messages.at(-1).payload.taskId,'');
        await chat.webview.receive({type:'assistant.send',taskId:'G1',text:'after logout'});
        assert.equal(sent,2);
        api.getTask=async id=>task(id);
        api.getAISubmissions=async()=>[{id:'checked',task_id:'G1',version:'1',
            solution_hash:createHash('sha256').update(code).digest('hex'),understanding:'pending'}];
        await AssistantPanel.follow('G1',code,async()=>code);
        assert.equal(chat.webview.messages.at(-1).payload.submissionId,'checked');
        code='def task_g1(): return 100';
        await chat.webview.receive({type:'assistant.start',taskId:'G1',mode:'defend'});
        assert.equal(created,1,'stale code must not start a paid defense');
        assert.match(chat.webview.messages.at(-1).payload.error,/Код изменился/);
        let resolveAccount;
        api.getAIAccount=()=>new Promise(resolve=>{resolveAccount=resolve;});
        const oldLogin=AssistantPanel.show('G1',code,'checked');
        await new Promise(resolve=>setImmediate(resolve));
        AssistantPanel.close(); // Login/server changes must stop subsequent model calls.
        resolveAccount(account);await oldLogin;
        assert.equal(created,1,'a detached session must not call models after auth reset');
        console.log('sidebar smoke: routing, unsaved code, task history, stale clicks, request races and auth reset passed');
    } finally {Module._load=originalLoad;}
})().catch(error=>{console.error(error);process.exitCode=1;});
