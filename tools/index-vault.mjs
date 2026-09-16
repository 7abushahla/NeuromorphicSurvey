import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

const site = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const vault = path.resolve(process.env.THESIS_VAULT || path.join(site, '../00-Vault'));
const literature = path.join(vault, '01-Literature');
const files = [];
function walk(dir) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    if (e.name.startsWith('.') || e.isSymbolicLink()) continue;
    const p = path.join(dir, e.name);
    if (e.isDirectory()) walk(p);
    else if (/\.(md|pdf)$/i.test(e.name) && !e.name.startsWith('_') && !p.includes('/_index/')) files.push(p);
  }
}
walk(literature);
for (const name of ['2026-09-14-literature-refresh-full-reports.md', '2026-09-14-literature-refresh-positioning.md', '2026-09-15-thesis-plan.md']) {
  const p = path.join(vault, '04-Writing', name); if (fs.existsSync(p)) files.push(p);
}
const categoryMap = { '01-Quantization':'Quantization / MPQ', '02-SNN-Fundamentals':'SNN foundations', '03-ANN-to-SNN-Conversion':'Conversion', '04-Hardware':'Hardware', '05-Neuromorphic-Background':'Neuromorphic background', '06-Applications':'Applications', '07-Tools':'Software', '08-Benchmarks':'Benchmarks', '10-NAS':'Architecture search' };
const manifest = {};
const records = files.map(p => {
  const relative = path.relative(vault,p);
  const id = crypto.createHash('sha256').update(relative).digest('hex').slice(0,20);
  const type = path.extname(p).slice(1);
  const raw = type === 'md' ? fs.readFileSync(p,'utf8') : '';
  const content = raw.replace(/^---\r?\n[\s\S]*?\r?\n---\r?\n/,'');
  const title = content.match(/^#\s+(.+)$/m)?.[1] ?? path.basename(p,path.extname(p)).replaceAll('_',' ');
  const authors = content.match(/\*\*Authors?\.?\*\*\s*(.+)/)?.[1]?.trim() ?? '';
  const venue = content.match(/\*\*Venue\.?\*\*\s*(.+)/)?.[1]?.trim() ?? '';
  const date = content.match(/\*\*Date\.?\*\*\s*(.+)/)?.[1]?.trim() ?? '';
  const categoryKey = relative.split(path.sep)[1];
  const category = relative.startsWith('04-Writing') ? 'Thesis synthesis' : relative.split(path.sep).length < 3 ? 'Vault navigation' : categoryMap[categoryKey] ?? categoryKey?.replace(/^\d+-/,'').replaceAll('-',' ') ?? 'Other';
  const urls = [...new Set((content.match(/https?:\/\/[^\s<>"\])]+/g) ?? []).map(u=>u.replace(/[.,;]+$/,'')))];
  const tags = [category];
  for (const [pattern,label] of [[/qcfs/i,'QCFS'],[/mixed|mpq|pascal|pseudosnn|mt-snn/i,'Mixed precision / timesteps'],[/loihi|lava|nxtf/i,'Loihi / Lava'],[/speck|dynap|sinabs/i,'Speck / Sinabs'],[/encoding|ttfs|phase|sigma|differential/i,'Encoding'],[/survey/i,'Survey'],[/spikingjelly/i,'SpikingJelly']]) {
    if (pattern.test(relative+' '+title)) tags.push(label);
  }
  manifest[id] = relative;
  return {id,title,type,category,tags,authors,venue,date,path:relative,urls,content,bytes:fs.statSync(p).size,evidence:type==='pdf'?'Local PDF, cataloged only':'Imported vault note, not revalidated'};
}).sort((a,b)=>a.title.localeCompare(b.title));
fs.mkdirSync(path.join(site,'public/data'),{recursive:true});
fs.writeFileSync(path.join(site,'public/data/vault.json'),JSON.stringify({generated:new Date().toISOString(),records},null,2));
fs.writeFileSync(path.join(site,'lib/vault-files.json'),JSON.stringify(manifest,null,2));
console.log(JSON.stringify({records:records.length,notes:records.filter(r=>r.type==='md').length,pdfs:records.filter(r=>r.type==='pdf').length,categories:[...new Set(records.map(r=>r.category))].sort()},null,2));
