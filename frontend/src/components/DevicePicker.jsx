import { useEffect,useState } from "react";
import { getDevices } from "../services/api";
export default function DevicePicker({value,onChange}){ const [devices,setDevices]=useState([]); useEffect(()=>{getDevices().then(setDevices).catch(()=>setDevices([]))},[]); return <select value={value} onChange={e=>onChange(e.target.value)}><option value="">Select device</option>{devices.map(d=><option key={d.id} value={d.id}>#{d.id} — {d.name}</option>)}</select> }
