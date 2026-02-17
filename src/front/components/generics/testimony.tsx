import { cn } from '@components/index';

export interface TestimonyProps {
    name?: string;
    image?: string;
    description?: string;
    testimony?: string;
    children?: string;
    className?: string;
}

export function Testimony({
    name,
    image,
    description,
    testimony,
    children,
    className,
    ...rest
}: TestimonyProps) {

    return (
        <div class="flex items-center gap-4">
            <div class="bg-[rgba(0,0,0,0.1)] rounded-sm p-4 flex flex-col gap-4">
                <div class="flex gap-4 items-center">
                    <img class="w-12 h-12 object-cover rounded-full" src={image} alt="Avatar"/>
                    <div>
                        <h5 class="font-semibold text-base">{name}</h5>
                        <p class="text-sm">{description}</p>
                    </div>
                </div>
                <p class="text-sm">{testimony}</p>
            </div>
        </div>
    );
}
